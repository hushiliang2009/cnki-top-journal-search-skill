from pathlib import Path
import asyncio
from datetime import date
import os
import subprocess
import sys

import pytest

from cnki_search_env.models import SearchStatus
from cnki_search_env.service import CnkiPublicSearchService
from cnki_search_env.session import PublicCnkiSession, SearchSnapshot


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "环境科学与工程学科顶尖期刊目录_v3.0.md"
FIXTURES = Path(__file__).with_name("fixtures")


class FakeSession:
    def __init__(self, html: str) -> None:
        self.html = html

    async def __aenter__(self) -> "FakeSession":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        return None

    async def search(self, query: str) -> SearchSnapshot:
        return SearchSnapshot(
            self.html, "https://kns.cnki.net/kns8s/defaultresult/index",
            "检索-中国知网", "题名 作者 来源 日期 数据库", 200,
        )


def test_service_returns_partial_when_incomplete_rows_exist() -> None:
    html = (FIXTURES / "public_incomplete_results.html").read_text(encoding="utf-8")
    service = CnkiPublicSearchService(session_factory=lambda: FakeSession(html), catalog=CATALOG)
    outcome = asyncio.run(service.search("数字化转型", limit=20))
    assert outcome.status.value == "partial"
    assert all(item.title and item.journal_raw and item.publication_year for item in outcome.records)
    assert outcome.incomplete_records


class CountingGate:
    def __init__(self) -> None:
        self.calls = 0

    async def wait(self) -> float:
        self.calls += 1
        return 0.0


class SequenceFactory:
    def __init__(self, snapshots: list[SearchSnapshot]) -> None:
        self.snapshots = snapshots
        self.calls = 0

    def __call__(self) -> "SequenceFactory":
        return self

    async def __aenter__(self) -> "SequenceFactory":
        self.calls += 1
        return self

    async def __aexit__(self, *_exc: object) -> None:
        return None

    async def search(self, _query: str) -> SearchSnapshot:
        return self.snapshots[self.calls - 1]


RESULT_PAGE_HTML = "<table class='result-table-list'></table>"
# 受限页（验证码、登录、429、403）不会携带 CNKI 结果表——正文里的受限措辞
# 只有在没有结果表时才是可信信号。
RESTRICTED_PAGE_HTML = "<main><div class='tip'></div></main>"


def _snapshot(
    *,
    url: str = "https://kns.cnki.net/kns8s/defaultresult/index",
    text: str = "题名 来源",
    status: int | None = 200,
    html: str = RESULT_PAGE_HTML,
) -> SearchSnapshot:
    return SearchSnapshot(html, url, "中国知网", text, status)


def test_network_error_retries_once_only() -> None:
    factory = SequenceFactory([_snapshot(status=500), _snapshot(status=500)])
    gate = CountingGate()
    outcome = asyncio.run(CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题"))
    assert outcome.status is SearchStatus.NETWORK_ERROR
    assert (factory.calls, gate.calls) == (2, 2)


def test_browser_preparation_finishes_before_search_timeout_starts() -> None:
    preparation_calls = 0

    async def prepare_browser() -> None:
        nonlocal preparation_calls
        preparation_calls += 1
        await asyncio.sleep(0.2)

    factory = SequenceFactory([
        _snapshot(text="未检索到相关文献", html=RESTRICTED_PAGE_HTML),
    ])
    service = CnkiPublicSearchService(
        session_factory=factory,
        catalog=CATALOG,
        gate=CountingGate(),
        search_timeout_seconds=0.15,
        browser_preparer=prepare_browser,
    )

    outcome = asyncio.run(service.search("主题"))

    assert outcome.status is SearchStatus.NO_RESULTS
    assert preparation_calls == 1


PlaywrightTimeoutBase = type(
    "TimeoutError", (RuntimeError,), {"__module__": "playwright._impl._errors"}
)


class DerivedPlaywrightTimeout(PlaywrightTimeoutBase):
    pass


class _Closable:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class GotoTimeoutFactory:
    def __init__(self) -> None:
        self.calls = 0
        self.resources: list[tuple[_Closable, _Closable, _Closable]] = []

    def __call__(self) -> PublicCnkiSession:
        self.calls += 1
        page = _Closable()
        page.goto = lambda *_args, **_kwargs: (_ for _ in ()).throw(DerivedPlaywrightTimeout("timeout"))  # type: ignore[attr-defined]
        context = _Closable()
        context.new_page = lambda: page  # type: ignore[attr-defined]
        browser = _Closable()
        browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]

        class Factory:
            def launch_ephemeral(self) -> _Closable:
                return browser

        session = PublicCnkiSession(browser_factory=Factory())
        self.resources.append((page, context, browser))
        return session


def test_playwright_style_timeout_retries_once_then_returns_network_error_and_closes_sessions() -> None:
    factory = GotoTimeoutFactory()
    gate = CountingGate()
    outcome = asyncio.run(CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题"))
    assert outcome.status is SearchStatus.NETWORK_ERROR
    assert (factory.calls, gate.calls) == (2, 2)
    assert all(page.closed and context.closed and browser.closed for page, context, browser in factory.resources)


@pytest.mark.parametrize(
    "snapshot, expected",
    [
        (_snapshot(text="429 Too Many Requests", html=RESTRICTED_PAGE_HTML), SearchStatus.RATE_LIMITED),
        (_snapshot(url="https://kns.cnki.net/captcha", text="请完成拼图验证"), SearchStatus.CHALLENGE_DETECTED),
        (_snapshot(url="https://login.cnki.net/", text="用户登录"), SearchStatus.LOGIN_REQUIRED),
        (_snapshot(text="403 Forbidden", html=RESTRICTED_PAGE_HTML), SearchStatus.FORBIDDEN),
        (_snapshot(url="https://example.invalid/", text="结构变化"), SearchStatus.PAGE_CONTRACT_CHANGED),
    ],
)
def test_restricted_or_changed_state_never_retries(snapshot: SearchSnapshot, expected: SearchStatus) -> None:
    factory = SequenceFactory([snapshot])
    gate = CountingGate()
    outcome = asyncio.run(CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题"))
    assert outcome.status is expected
    assert (factory.calls, gate.calls) == (1, 1)


def test_cache_hit_skips_session_and_gate() -> None:
    factory = SequenceFactory([_snapshot(text="未检索到相关文献", html=RESTRICTED_PAGE_HTML)])
    gate = CountingGate()
    service = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate)
    assert asyncio.run(service.search("主题")).status is SearchStatus.NO_RESULTS
    assert asyncio.run(service.search("主题")).status is SearchStatus.NO_RESULTS
    assert (factory.calls, gate.calls) == (1, 1)


def test_cache_hit_rewrites_outcome_query_to_current_normalized_request() -> None:
    factory = SequenceFactory([_snapshot(text="未检索到相关文献", html=RESTRICTED_PAGE_HTML)])
    service = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=CountingGate())
    first = asyncio.run(service.search("  ＡＢＣ　主题  "))
    second = asyncio.run(service.search("abc\t主题"))
    assert (first.query, second.query) == ("ABC 主题", "abc 主题")
    assert factory.calls == 1


def test_service_returns_partial_for_future_year_beyond_shared_range() -> None:
    year = date.today().year + 2
    html = (
        "<table class='result-table-list'><tr>"
        "<td class='seq'>1</td><td class='name'><a>题录</a></td>"
        "<td class='source'><a>期刊</a></td><td class='date'>"
        f"{year}</td><td class='data'>期刊</td></tr></table>"
    )
    outcome = asyncio.run(CnkiPublicSearchService(
        session_factory=lambda: FakeSession(html), catalog=CATALOG
    ).search("主题"))
    assert outcome.status is SearchStatus.PARTIAL
    assert outcome.records == []
    assert len(outcome.incomplete_records) == 1


def test_missing_catalog_reports_config_error_without_touching_cnki() -> None:
    """目录缺失是部署配置错误：不得谎报 network_error，也不得白打两次 CNKI。"""
    factory = SequenceFactory([_snapshot(), _snapshot()])
    gate = CountingGate()
    outcome = asyncio.run(CnkiPublicSearchService(
        session_factory=factory, catalog=ROOT / "references" / "不存在的目录.md", gate=gate
    ).search("主题"))

    assert outcome.status is SearchStatus.CONFIGURATION_ERROR
    assert (factory.calls, gate.calls) == (0, 0)
    assert outcome.warnings == ["配置错误"]


def test_invalid_catalog_reports_configuration_error_without_touching_cnki(tmp_path: Path) -> None:
    invalid = tmp_path / "环境科学与工程学科顶尖期刊目录_v3.0.md"
    invalid.write_text("# invalid\n", encoding="utf-8")
    factory = SequenceFactory([_snapshot()])
    gate = CountingGate()

    outcome = asyncio.run(CnkiPublicSearchService(session_factory=factory, catalog=invalid, gate=gate).search("主题"))

    assert outcome.status is SearchStatus.CONFIGURATION_ERROR
    assert (factory.calls, gate.calls) == (0, 0)
    assert str(tmp_path) not in "\n".join(outcome.warnings)


def test_missing_catalog_short_circuits_cnki_in_both_runtime_layouts() -> None:
    source_roots = (ROOT / "scripts", ROOT / "mcpb" / "src")
    program = """
import asyncio
from pathlib import Path
from cnki_search_env.models import SearchStatus
from cnki_search_env.service import CnkiPublicSearchService

class Gate:
    calls = 0
    async def wait(self):
        type(self).calls += 1

class Session:
    calls = 0
    async def __aenter__(self):
        type(self).calls += 1
        return self
    async def __aexit__(self, *_exc):
        return None

gate = Gate()
outcome = asyncio.run(CnkiPublicSearchService(
    session_factory=Session,
    catalog=Path('missing-catalog.md'),
    gate=gate,
).search('主题'))
assert outcome.status is SearchStatus.CONFIGURATION_ERROR
assert (Session.calls, Gate.calls) == (0, 0)
assert all('C:\\\\' not in warning and '/home/' not in warning for warning in outcome.warnings)
"""
    for source_root in source_roots:
        completed = subprocess.run(
            [sys.executable, "-c", program],
            cwd=source_root,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr


def test_warnings_never_leak_local_absolute_paths() -> None:
    outcome = asyncio.run(CnkiPublicSearchService(
        session_factory=lambda: FakeSession(""),
        catalog=ROOT / "references" / "不存在的目录.md",
    ).search("主题"))

    for warning in outcome.warnings:
        assert str(ROOT) not in warning
        assert "/home/" not in warning and "C:\\" not in warning


def test_browser_unavailable_is_structured_and_not_retried() -> None:
    """浏览器启动失败不是 OSError 子类，不转换就会裸穿 MCP 边界。"""
    from cnki_search_env.browser import BrowserUnavailableError

    gate = CountingGate()

    class FailingFactory:
        calls = 0

        def __call__(self) -> "FailingFactory":
            return self

        async def __aenter__(self) -> "FailingFactory":
            type(self).calls += 1
            raise BrowserUnavailableError("浏览器不可用：请在 MCP 运行环境中执行 xxx")

        async def __aexit__(self, *_exc: object) -> None:
            return None

    outcome = asyncio.run(CnkiPublicSearchService(
        session_factory=FailingFactory(), catalog=CATALOG, gate=gate
    ).search("主题"))

    assert outcome.status is SearchStatus.CONFIGURATION_ERROR
    assert FailingFactory.calls == 1, "安装类故障重试无意义"
    assert outcome.warnings == ["浏览器不可用"]


def test_restricted_states_carry_actionable_fallback_hint() -> None:
    """受限状态不等于"该主题无文献"，必须给出可操作的替代路径。"""
    factory = SequenceFactory(
        [_snapshot(url="https://kns.cnki.net/verify/home", text="", html="<main></main>")]
    )
    outcome = asyncio.run(CnkiPublicSearchService(
        session_factory=factory, catalog=CATALOG, gate=CountingGate()
    ).search("供应链金融"))

    assert outcome.status is SearchStatus.CHALLENGE_DETECTED
    warning = outcome.warnings[0]
    for phrase in (
        "知网安全验证已阻止本次检索",
        "已停止请求",
        "不要刷新、重试或切换代理",
        "ai4scholar",
        "浏览器手动检索下载",
    ):
        assert phrase in warning
    assert not any(token in warning for token in ("C:\\", "/home/", "http", "cookie"))


def test_challenge_warning_is_actionable_in_both_runtime_layouts() -> None:
    roots = (ROOT / "scripts", ROOT / "mcpb" / "src")
    program = """
import asyncio
from pathlib import Path
from cnki_search_env.models import SearchStatus
from cnki_search_env.service import CnkiPublicSearchService

class Snapshot:
    html = '<main></main>'
    url = 'https://kns.cnki.net/verify/home'
    title = '安全验证'
    visible_text = ''
    http_status = 200
    def state_arguments(self):
        return {
            'url': self.url,
            'title': self.title,
            'visible_text': self.visible_text,
            'http_status': self.http_status,
            'has_result_table': False,
        }

class Session:
    async def __aenter__(self):
        return self
    async def __aexit__(self, *_exc):
        return None
    async def search(self, _query):
        return Snapshot()

catalog = Path('references/环境科学与工程学科顶尖期刊目录_v3.0.md')
if not catalog.exists():
    catalog = Path('../references/环境科学与工程学科顶尖期刊目录_v3.0.md')
outcome = asyncio.run(CnkiPublicSearchService(
    session_factory=Session,
    catalog=catalog,
).search('topic'))
assert outcome.status is SearchStatus.CHALLENGE_DETECTED
warning = outcome.warnings[0]
for phrase in ('知网安全验证已阻止本次检索', '已停止请求', '不要刷新、重试或切换代理', 'ai4scholar', '浏览器手动检索下载'):
    assert phrase in warning
assert not any(token in warning for token in ('C:\\\\', '/home/', 'http', 'cookie'))
"""
    for root in roots:
        completed = subprocess.run(
            [sys.executable, "-c", program],
            cwd=root,
            env=os.environ | {"PYTHONPATH": str(root)},
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
