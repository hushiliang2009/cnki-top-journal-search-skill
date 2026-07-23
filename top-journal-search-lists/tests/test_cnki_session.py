import os
import subprocess
import sys
from pathlib import Path

import pytest

import cnki_search.session as session_module
from cnki_search.browser import BrowserFactory
from cnki_search.models import SearchStatus
from cnki_search.session import PublicCnkiSession


ROOT = Path(__file__).resolve().parents[1]


def test_public_session_uses_only_cnki_home() -> None:
    assert session_module.CNKI_HOME_URL == "https://www.cnki.net/"
    source = Path(session_module.__file__).read_text(encoding="utf-8").casefold()
    assert "webvpn" not in source
    assert "advsearch" not in source
    assert "brief/grid" not in source


@pytest.mark.parametrize(
    ("url", "text", "expected"),
    [
        ("https://kns.cnki.net/captcha", "请完成拼图验证", SearchStatus.CHALLENGE_DETECTED),
        ("https://login.cnki.net/", "用户登录", SearchStatus.LOGIN_REQUIRED),
        ("https://kns.cnki.net/kns8s/authserver/login", "普通认证页", SearchStatus.LOGIN_REQUIRED),
        ("https://kns.cnki.net/", "403 Forbidden", SearchStatus.FORBIDDEN),
        ("https://kns.cnki.net/", "访问过于频繁", SearchStatus.RATE_LIMITED),
        ("https://kns.cnki.net/", "未检索到相关文献", SearchStatus.NO_RESULTS),
    ],
)
def test_restrictions_stop_without_fallback(url: str, text: str, expected: SearchStatus) -> None:
    assert session_module.classify_public_search_state(url=url, title="", visible_text=text) is expected


class FakeBrowserType:
    def __init__(self) -> None:
        self.launch_kwargs: dict[str, object] = {}

    def launch(self, **kwargs: object) -> object:
        self.launch_kwargs = kwargs
        return object()


class FakePlaywright:
    def __init__(self) -> None:
        self.chromium = FakeBrowserType()


def test_browser_launch_is_headless_and_has_no_persistent_state() -> None:
    fake = FakePlaywright()
    BrowserFactory(fake).launch_ephemeral()
    assert fake.chromium.launch_kwargs["headless"] is True
    assert fake.chromium.launch_kwargs["args"] == ["--no-proxy-server", "--proxy-bypass-list=*"]
    assert "user_data_dir" not in fake.chromium.launch_kwargs
    assert "storage_state" not in fake.chromium.launch_kwargs
    assert "proxy" not in fake.chromium.launch_kwargs


class _Closable:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def stop(self) -> None:
        self.closed = True


PlaywrightTimeoutBase = type(
    "TimeoutError", (RuntimeError,), {"__module__": "playwright._impl._errors"}
)


class DerivedPlaywrightTimeout(PlaywrightTimeoutBase):
    pass


class _GotoTimeoutPage(_Closable):
    def goto(self, _url: str, *, wait_until: str) -> object:
        assert wait_until == "domcontentloaded"
        raise DerivedPlaywrightTimeout("navigation timed out")


def test_session_converts_playwright_style_timeout_and_closes_initialization_resources() -> None:
    page = _GotoTimeoutPage()
    context = _Closable()
    context.new_page = lambda: page  # type: ignore[attr-defined]
    browser = _Closable()
    browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]
    playwright = _Closable()

    class Factory:
        def launch_ephemeral(self) -> _Closable:
            return browser

    session = PublicCnkiSession(browser_factory=Factory())
    session._playwright = playwright
    with pytest.raises(RuntimeError) as raised:
        session.__enter__()
    assert type(raised.value).__name__ == "TransientBrowserError"
    assert page.closed and context.closed and browser.closed and playwright.closed
    assert session.page is None and session.context is None and session.browser is None


def test_challenge_classifier_ignores_ordinary_safety_description() -> None:
    assert session_module.classify_public_search_state(
        url="https://kns.cnki.net/kns8s/defaultresult/", title="", visible_text="安全验证说明"
    ) is SearchStatus.PAGE_CONTRACT_CHANGED


def test_challenge_classifier_accepts_captcha_url_without_generic_text() -> None:
    assert session_module.classify_public_search_state(
        url="https://kns.cnki.net/captcha", title="", visible_text="请稍候"
    ) is SearchStatus.CHALLENGE_DETECTED


@pytest.mark.parametrize(
    ("url", "title", "text", "http_status", "expected"),
    [
        (
            "https://kns.cnki.net/kns8s/defaultresult/index",
            "拒绝访问 用户登录 统一身份认证",
            "题名 来源 访问过于频繁 无权访问 拒绝访问 用户登录 统一身份认证",
            200,
            SearchStatus.SUCCESS,
        ),
        (
            "https://kns.cnki.net/kns8s/defaultresult/index",
            "中国知网",
            "题名 来源",
            403,
            SearchStatus.FORBIDDEN,
        ),
        (
            "https://kns.cnki.net/verify/home",
            "安全验证",
            "",
            200,
            SearchStatus.CHALLENGE_DETECTED,
        ),
        (
            "https://www.cnki.net/",
            "中国知网",
            "中国知网公开首页",
            200,
            SearchStatus.PAGE_CONTRACT_CHANGED,
        ),
        (
            "https://kns.cnki.net/kns8s/defaultresult/index",
            "中国知网",
            "普通页面说明：请完成安全验证后可继续使用服务",
            200,
            SearchStatus.PAGE_CONTRACT_CHANGED,
        ),
    ],
)
def test_public_state_truth_table_prioritizes_status_and_result_structure(
    url: str, title: str, text: str, http_status: int, expected: SearchStatus,
) -> None:
    assert session_module.classify_public_search_state(
        url=url,
        title=title,
        visible_text=text,
        http_status=http_status,
        has_result_table=expected is SearchStatus.SUCCESS,
    ) is expected


def test_state_truth_table_runs_in_both_runtime_layouts() -> None:
    roots = (ROOT / "scripts", ROOT / "mcpb" / "src")
    program = """
from cnki_search.models import SearchStatus
from cnki_search.session import classify_public_search_state

result_url = 'https://kns.cnki.net/kns8s/defaultresult/index'
assert classify_public_search_state(
        url=result_url,
        title='拒绝访问 用户登录',
        visible_text='题名 来源 无权访问 访问过于频繁 用户登录',
        http_status=200,
        has_result_table=True,
    ) is SearchStatus.SUCCESS
assert classify_public_search_state(
    url='https://kns.cnki.net/verify/home', title='安全验证', visible_text='', http_status=200,
) is SearchStatus.CHALLENGE_DETECTED
assert classify_public_search_state(
    url=result_url, title='中国知网', visible_text='题名 来源', http_status=403,
) is SearchStatus.FORBIDDEN
assert classify_public_search_state(
    url='https://www.cnki.net/', title='中国知网', visible_text='首页', http_status=200,
) is SearchStatus.PAGE_CONTRACT_CHANGED
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


def test_result_table_structure_controls_success_and_body_restriction_fallback_in_both_layouts() -> None:
    roots = (ROOT / "scripts", ROOT / "mcpb" / "src")
    program = """
from cnki_search.models import SearchStatus
from cnki_search.session import SearchSnapshot, classify_public_search_state

url = 'https://kns.cnki.net/kns8s/defaultresult/index'
without_table = SearchSnapshot('<main></main>', url, '中国知网', '题名 来源', 200)
assert without_table.has_result_table is False
assert classify_public_search_state(**without_table.state_arguments()) is SearchStatus.PAGE_CONTRACT_CHANGED
with_table = SearchSnapshot(
    '<table class="result-table-list"><tr><td>题名</td></tr></table>',
    url,
    '中国知网',
    '无权访问 访问过于频繁',
    200,
)
assert with_table.has_result_table is True
assert classify_public_search_state(**with_table.state_arguments()) is SearchStatus.SUCCESS
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


class RestrictedPage:
    def __init__(self, text: str, response_status: int | None = None) -> None:
        self.url = "https://www.cnki.net/"
        self.text = text
        self.response_status = response_status
        self.box_accessed = False

    def title(self) -> str:
        return "中国知网"

    def goto(self, url: str, *, wait_until: str) -> object | None:
        assert (url, wait_until) == (session_module.CNKI_HOME_URL, "domcontentloaded")
        if self.response_status is None:
            return None
        return type("Response", (), {"status": self.response_status})()

    def locator(self, selector: str) -> "RestrictedPage":
        assert selector == "body"
        return self

    def inner_text(self, *, timeout: int) -> str:
        assert timeout == 10_000
        return self.text

    def content(self) -> str:
        return "<main>restricted</main>"

    def get_by_role(self, *_args: object, **_kwargs: object) -> object:
        self.box_accessed = True
        raise AssertionError("受限首页不得访问主题框")

    def get_by_text(self, *_args: object, **_kwargs: object) -> object:
        self.box_accessed = True
        raise AssertionError("受限首页不得访问主题框")


def test_session_returns_initial_restriction_before_theme_contract_and_closes_resources() -> None:
    page = RestrictedPage("403 Forbidden")
    context = _Closable()
    context.new_page = lambda: page  # type: ignore[attr-defined]
    browser = _Closable()
    browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]

    class Factory:
        def launch_ephemeral(self) -> _Closable:
            return browser

    session = PublicCnkiSession(browser_factory=Factory())
    with session:
        snapshot = session.search("主题")
        assert session_module.classify_public_search_state(**snapshot.state_arguments()) is SearchStatus.FORBIDDEN
    assert page.box_accessed is False
    assert context.closed and browser.closed
@pytest.mark.parametrize(
    ("response_status", "expected"),
    [(403, SearchStatus.FORBIDDEN), (429, SearchStatus.RATE_LIMITED)],
)
def test_session_uses_initial_response_status_before_theme_contract(
    response_status: int, expected: SearchStatus,
) -> None:
    page = RestrictedPage("", response_status)
    context = _Closable()
    context.new_page = lambda: page  # type: ignore[attr-defined]
    browser = _Closable()
    browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]

    class Factory:
        def launch_ephemeral(self) -> _Closable:
            return browser

    session = PublicCnkiSession(browser_factory=Factory())
    with session:
        snapshot = session.search("主题")
        assert snapshot.http_status == response_status
        assert session_module.classify_public_search_state(**snapshot.state_arguments()) is expected
    assert page.box_accessed is False
    assert context.closed and browser.closed
