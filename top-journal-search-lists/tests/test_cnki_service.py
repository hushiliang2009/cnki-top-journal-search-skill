from pathlib import Path
from datetime import date

import pytest

from cnki_search.models import SearchStatus
from cnki_search.service import CnkiPublicSearchService
from cnki_search.session import PublicCnkiSession, SearchSnapshot


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "Academic_Journal_Master_Directory_20260715.md"
FIXTURES = Path(__file__).with_name("fixtures")


class FakeSession:
    def __init__(self, html: str) -> None:
        self.html = html

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def search(self, query: str) -> SearchSnapshot:
        return SearchSnapshot(
            self.html, "https://kns.cnki.net/kns8s/defaultresult/index",
            "检索-中国知网", "题名 作者 来源 日期 数据库", 200,
        )


def test_service_returns_partial_when_incomplete_rows_exist() -> None:
    html = (FIXTURES / "public_incomplete_results.html").read_text(encoding="utf-8")
    service = CnkiPublicSearchService(session_factory=lambda: FakeSession(html), catalog=CATALOG)
    outcome = service.search("数字化转型", limit=20)
    assert outcome.status.value == "partial"
    assert all(item.title and item.journal_raw and item.publication_year for item in outcome.records)
    assert outcome.incomplete_records


class CountingGate:
    def __init__(self) -> None:
        self.calls = 0

    def wait(self) -> float:
        self.calls += 1
        return 0.0


class SequenceFactory:
    def __init__(self, snapshots: list[SearchSnapshot]) -> None:
        self.snapshots = snapshots
        self.calls = 0

    def __call__(self) -> "SequenceFactory":
        return self

    def __enter__(self) -> "SequenceFactory":
        self.calls += 1
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def search(self, _query: str) -> SearchSnapshot:
        return self.snapshots[self.calls - 1]


def _snapshot(*, url: str = "https://kns.cnki.net/kns8s/defaultresult/index", text: str = "题名 来源", status: int | None = 200) -> SearchSnapshot:
    return SearchSnapshot("<table class='result-table-list'></table>", url, "中国知网", text, status)


def test_network_error_retries_once_only() -> None:
    factory = SequenceFactory([_snapshot(status=500), _snapshot(status=500)])
    gate = CountingGate()
    outcome = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题")
    assert outcome.status is SearchStatus.NETWORK_ERROR
    assert (factory.calls, gate.calls) == (2, 2)


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
    outcome = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题")
    assert outcome.status is SearchStatus.NETWORK_ERROR
    assert (factory.calls, gate.calls) == (2, 2)
    assert all(page.closed and context.closed and browser.closed for page, context, browser in factory.resources)


@pytest.mark.parametrize(
    "snapshot, expected",
    [
        (_snapshot(text="429 Too Many Requests"), SearchStatus.RATE_LIMITED),
        (_snapshot(url="https://kns.cnki.net/captcha", text="请完成拼图验证"), SearchStatus.CHALLENGE_DETECTED),
        (_snapshot(url="https://login.cnki.net/", text="用户登录"), SearchStatus.LOGIN_REQUIRED),
        (_snapshot(text="403 Forbidden"), SearchStatus.FORBIDDEN),
        (_snapshot(url="https://example.invalid/", text="结构变化"), SearchStatus.PAGE_CONTRACT_CHANGED),
    ],
)
def test_restricted_or_changed_state_never_retries(snapshot: SearchSnapshot, expected: SearchStatus) -> None:
    factory = SequenceFactory([snapshot])
    gate = CountingGate()
    outcome = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题")
    assert outcome.status is expected
    assert (factory.calls, gate.calls) == (1, 1)


def test_cache_hit_skips_session_and_gate() -> None:
    factory = SequenceFactory([_snapshot(text="未检索到相关文献")])
    gate = CountingGate()
    service = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate)
    assert service.search("主题").status is SearchStatus.NO_RESULTS
    assert service.search("主题").status is SearchStatus.NO_RESULTS
    assert (factory.calls, gate.calls) == (1, 1)


def test_service_returns_partial_for_future_year_beyond_shared_range() -> None:
    year = date.today().year + 2
    html = (
        "<table class='result-table-list'><tr>"
        "<td class='seq'>1</td><td class='name'><a>题录</a></td>"
        "<td class='source'><a>期刊</a></td><td class='date'>"
        f"{year}</td><td class='data'>期刊</td></tr></table>"
    )
    outcome = CnkiPublicSearchService(
        session_factory=lambda: FakeSession(html), catalog=CATALOG
    ).search("主题")
    assert outcome.status is SearchStatus.PARTIAL
    assert outcome.records == []
    assert len(outcome.incomplete_records) == 1
