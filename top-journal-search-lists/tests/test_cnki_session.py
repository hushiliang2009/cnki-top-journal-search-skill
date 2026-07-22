from pathlib import Path

import pytest

import cnki_search.session as session_module
from cnki_search.browser import BrowserFactory
from cnki_search.models import SearchStatus
from cnki_search.session import PublicCnkiSession


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
    assert "user_data_dir" not in fake.chromium.launch_kwargs
    assert "storage_state" not in fake.chromium.launch_kwargs
    assert "proxy" not in fake.chromium.launch_kwargs


class _Closable:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class RestrictedPage:
    def __init__(self, text: str) -> None:
        self.url = "https://www.cnki.net/"
        self.text = text
        self.box_accessed = False

    def title(self) -> str:
        return "中国知网"

    def goto(self, url: str, *, wait_until: str) -> None:
        assert (url, wait_until) == (session_module.CNKI_HOME_URL, "domcontentloaded")

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
