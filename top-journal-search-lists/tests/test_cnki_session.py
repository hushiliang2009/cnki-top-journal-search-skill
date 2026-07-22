from pathlib import Path

import pytest

import cnki_search.session as session_module
from cnki_search.browser import BrowserFactory
from cnki_search.models import SessionStatus
from cnki_search.session import (
    CnkiSession,
    DIRECT_CNKI_SEARCH_URL,
    HHU_CNKI_SEARCH_URL,
    classify_public_state,
    resolve_search_url,
)


FIXTURES = Path(__file__).with_name("fixtures")
HHU_NEW_SEARCH_URL = (
    "https://webvpn.hhu.edu.cn/https/"
    "77726476706e69737468656265737421fbf952d2243e635930068cb8/kns8s/AdvSearch"
)


def test_resolve_search_url_uses_new_entry_only() -> None:
    assert resolve_search_url("https://kns.cnki.net/") == DIRECT_CNKI_SEARCH_URL
    assert resolve_search_url("https://webvpn.hhu.edu.cn/") == HHU_CNKI_SEARCH_URL
    assert DIRECT_CNKI_SEARCH_URL == "https://kns.cnki.net/kns8s/AdvSearch"
    assert HHU_CNKI_SEARCH_URL == HHU_NEW_SEARCH_URL
    assert resolve_search_url("https://example.com/") is None


class RecordingPage:
    def __init__(
        self,
        url: str,
        *,
        redirected_url: str | None = None,
        title: str = "中国知网 高级检索",
        visible_text: str = "中国知网 高级检索",
    ) -> None:
        self.url = url
        self.visited: list[str] = []
        self.redirected_url = redirected_url
        self._title = title
        self._visible_text = visible_text

    def goto(self, url: str, *, wait_until: str) -> None:
        assert wait_until == "domcontentloaded"
        self.visited.append(url)
        self.url = self.redirected_url or url

    def title(self) -> str:
        return self._title

    def locator(self, selector: str):
        assert selector == "body"
        return self

    def inner_text(self, *, timeout: int) -> str:
        assert timeout == 5_000
        return self._visible_text


def test_session_opens_new_search_for_webvpn() -> None:
    page = RecordingPage("https://webvpn.hhu.edu.cn/")
    session = CnkiSession()
    session.page = page

    assert session.open_search() is SessionStatus.READY
    assert page.visited == [HHU_CNKI_SEARCH_URL]


def test_session_rejects_unrelated_host() -> None:
    page = RecordingPage("https://example.com/")
    session = CnkiSession()
    session.page = page

    assert session.open_search() is SessionStatus.SESSION_EXPIRED
    assert page.visited == []


def test_session_rejects_redirected_lookalike_host() -> None:
    page = RecordingPage(
        "https://webvpn.hhu.edu.cn/",
        redirected_url="https://example.com/kns8s/AdvSearch",
    )
    session = CnkiSession()
    session.page = page

    assert session.open_search() is SessionStatus.SESSION_EXPIRED


def test_session_rejects_redirected_path_change() -> None:
    page = RecordingPage(
        "https://webvpn.hhu.edu.cn/",
        redirected_url="https://webvpn.hhu.edu.cn/kns8s/AdvSearch/redirected",
    )
    session = CnkiSession()
    session.page = page

    assert session.open_search() is SessionStatus.SESSION_EXPIRED


def test_session_rejects_new_search_without_stable_visible_marker() -> None:
    page = RecordingPage(
        "https://kns.cnki.net/",
        title="",
        visible_text="",
    )
    session = CnkiSession()
    session.page = page

    assert session.open_search() is SessionStatus.SESSION_EXPIRED


class FakeBrowserType:
    def __init__(self) -> None:
        self.launch_kwargs: dict = {}

    def launch(self, **kwargs):
        self.launch_kwargs = kwargs
        return object()


class FakePlaywright:
    def __init__(self) -> None:
        self.chromium = FakeBrowserType()


def test_browser_launch_is_visible_and_ephemeral() -> None:
    fake = FakePlaywright()
    BrowserFactory(fake).launch_visible()
    assert fake.chromium.launch_kwargs["headless"] is False
    assert "user_data_dir" not in fake.chromium.launch_kwargs
    assert "storage_state" not in fake.chromium.launch_kwargs


@pytest.mark.parametrize(
    ("fixture", "url", "expected"),
    [
        ("login.html", "https://webvpn.hhu.edu.cn/authserver/login", SessionStatus.LOGIN_REQUIRED),
        ("captcha.html", "https://webvpn.hhu.edu.cn/verify", SessionStatus.CAPTCHA),
        ("advanced.html", "https://webvpn.hhu.edu.cn/https/cnki", SessionStatus.READY),
    ],
)
def test_status_from_public_page_state(fixture: str, url: str, expected: SessionStatus) -> None:
    html = (FIXTURES / fixture).read_text(encoding="utf-8")
    assert classify_public_state(url=url, title="", visible_text=html) is expected


def test_status_classifier_does_not_accept_form_values() -> None:
    with pytest.raises(TypeError):
        classify_public_state(url="x", title="x", visible_text="x", password="secret")


class CaptchaPage:
    url = HHU_NEW_SEARCH_URL

    def title(self) -> str:
        return ""

    def locator(self, selector: str):
        assert selector == "body"
        return self

    def inner_text(self, *, timeout: int) -> str:
        assert timeout == 5_000
        return ""


def test_session_keeps_captcha_status_without_search_page_recovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        session_module,
        "classify_public_state",
        lambda **_kwargs: SessionStatus.CAPTCHA,
    )
    session = CnkiSession()
    session.page = CaptchaPage()

    assert session.status() is SessionStatus.CAPTCHA


@pytest.mark.parametrize("ordinary_number", ["429", "403"])
def test_ready_cnki_page_does_not_treat_bare_numbers_as_http_errors(
    ordinary_number: str,
) -> None:
    status = classify_public_state(
        url="https://webvpn.hhu.edu.cn/https/cnki/",
        title="中国知网",
        visible_text=f"高级检索 期刊目录页 {ordinary_number} 种",
    )
    assert status is SessionStatus.READY
