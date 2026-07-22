from pathlib import Path

import pytest

import cnki_search.session as session_module
from cnki_search.browser import BrowserFactory
from cnki_search.models import SessionStatus
from cnki_search.session import (
    DIRECT_CNKI_OLD_SEARCH_URL,
    HHU_CNKI_OLD_SEARCH_URL,
    CnkiSession,
    classify_public_state,
    resolve_old_search_url,
)


FIXTURES = Path(__file__).with_name("fixtures")


def test_session_module_exposes_old_search_contract() -> None:
    assert hasattr(session_module, "DIRECT_CNKI_OLD_SEARCH_URL")
    assert hasattr(session_module, "HHU_CNKI_OLD_SEARCH_URL")
    assert hasattr(session_module, "resolve_old_search_url")


def test_hhu_cnki_home_url_does_not_fix_record_visit_parameter() -> None:
    assert "wrdrecordvisit" not in session_module.HHU_CNKI_URL


@pytest.mark.parametrize(
    ("current_url", "expected"),
    [
        ("https://webvpn.hhu.edu.cn/", HHU_CNKI_OLD_SEARCH_URL),
        ("https://kns.cnki.net/starter/index", DIRECT_CNKI_OLD_SEARCH_URL),
    ],
)
def test_resolve_old_search_url_by_current_session(
    current_url: str,
    expected: str,
) -> None:
    assert resolve_old_search_url(current_url) == expected
    assert "wrdrecordvisit" not in expected


def test_resolve_old_search_url_rejects_unrelated_page() -> None:
    assert resolve_old_search_url("https://example.com/") is None


def test_session_exposes_old_search_navigation() -> None:
    assert hasattr(CnkiSession, "open_old_search")


class ReadyBody:
    def inner_text(self, timeout: int) -> str:
        assert timeout == 5_000
        return "中国知网 高级检索 专业检索"


class RecordingOldSearchPage:
    def __init__(self, current_url: str) -> None:
        self.url = current_url
        self.visited: list[str] = []

    def goto(self, url: str, *, wait_until: str) -> None:
        assert wait_until == "domcontentloaded"
        self.visited.append(url)
        self.url = url

    def title(self) -> str:
        return "高级检索-中国知网"

    def locator(self, selector: str) -> ReadyBody:
        assert selector == "body"
        return ReadyBody()


def test_session_opens_old_search_for_webvpn() -> None:
    session = CnkiSession()
    session.page = RecordingOldSearchPage("https://webvpn.hhu.edu.cn/")
    assert session.open_old_search() is SessionStatus.READY
    assert session.page.visited == [HHU_CNKI_OLD_SEARCH_URL]


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


def test_ready_cnki_page_wins_over_incidental_security_help_text() -> None:
    status = classify_public_state(
        url="https://webvpn.hhu.edu.cn/https/cnki/",
        title="中国知网",
        visible_text="高级检索 安全验证服务说明",
    )
    assert status is SessionStatus.READY


def test_old_advanced_search_with_captcha_id_query_parameter_is_ready() -> None:
    status = classify_public_state(
        url=(
            "https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch?"
            "dbcode=CJZK&captchaId=completed-puzzle"
        ),
        title="高级检索-中国知网",
        visible_text="中国知网 高级检索 专业检索",
    )
    assert status is SessionStatus.READY


def test_unrelated_path_with_captcha_id_query_parameter_is_captcha() -> None:
    status = classify_public_state(
        url="https://webvpn.hhu.edu.cn/unrelated?captchaId=completed-puzzle",
        title="高级检索-中国知网",
        visible_text="中国知网 高级检索 专业检索",
    )
    assert status is SessionStatus.CAPTCHA


def test_old_advanced_search_with_captcha_type_query_parameter_is_captcha() -> None:
    status = classify_public_state(
        url=(
            "https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch?"
            "dbcode=CJZK&captchaType=blockPuzzle"
        ),
        title="高级检索-中国知网",
        visible_text="中国知网 高级检索 专业检索",
    )
    assert status is SessionStatus.CAPTCHA


def test_verification_path_with_captcha_query_parameter_is_captcha() -> None:
    status = classify_public_state(
        url="https://webvpn.hhu.edu.cn/verify/home?captchaType=blockPuzzle",
        title="安全验证",
        visible_text="",
    )
    assert status is SessionStatus.CAPTCHA


def test_explicit_slider_verification_beats_ready_cnki_content() -> None:
    status = classify_public_state(
        url="https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch",
        title="高级检索-中国知网",
        visible_text="中国知网 高级检索 拖动下方拼图完成验证 安全验证",
    )
    assert status is SessionStatus.CAPTCHA


class OldSearchContractLocator:
    def __init__(self, *, text: str = "", count: int = 0, error: Exception | None = None) -> None:
        self._text = text
        self._count = count
        self._error = error

    def inner_text(self, timeout: int) -> str:
        assert timeout == 5_000
        return self._text

    def count(self) -> int:
        if self._error is not None:
            raise self._error
        return self._count


class OldSearchContractPage:
    def __init__(
        self,
        *,
        url: str = "https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch?dbcode=CJZK",
        title: str = "检索--中国知网",
        text: str = "中国知网检索页面的普通安全说明",
        grade_count: int = 1,
        major_count: int = 1,
        locator_error: Exception | None = None,
    ) -> None:
        self.url = url
        self._title = title
        self._text = text
        self._grade_count = grade_count
        self._major_count = major_count
        self._locator_error = locator_error

    def title(self) -> str:
        return self._title

    def locator(self, selector: str) -> OldSearchContractLocator:
        if selector == "body":
            return OldSearchContractLocator(text=self._text)
        if selector == 'li[name="gradeSearch"]':
            return OldSearchContractLocator(count=self._grade_count, error=self._locator_error)
        if selector == 'li[name="majorSearch"]':
            return OldSearchContractLocator(count=self._major_count, error=self._locator_error)
        raise AssertionError(f"unexpected selector: {selector}")


def test_status_recovers_old_search_contract_after_public_captcha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        session_module,
        "classify_public_state",
        lambda **_kwargs: SessionStatus.CAPTCHA,
    )
    session = CnkiSession()
    session.page = OldSearchContractPage()

    assert session.status() is SessionStatus.READY


def test_status_recovers_old_search_contract_with_residual_captcha_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        session_module,
        "classify_public_state",
        lambda **_kwargs: SessionStatus.CAPTCHA,
    )
    session = CnkiSession()
    session.page = OldSearchContractPage(
        url=(
            "https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch?"
            "dbcode=CJZK&captchaId=completed-puzzle"
        )
    )

    assert session.status() is SessionStatus.READY


@pytest.mark.parametrize(
    "page",
    [
        OldSearchContractPage(title="安全验证--中国知网"),
        OldSearchContractPage(grade_count=0),
        OldSearchContractPage(major_count=0),
        OldSearchContractPage(text="中国知网 请完成拼图验证"),
        OldSearchContractPage(url="https://webvpn.hhu.edu.cn/verify/home"),
        OldSearchContractPage(
            url=(
                "https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch?"
                "dbcode=CJZK&captchaType=blockPuzzle"
            )
        ),
        OldSearchContractPage(
            url=(
                "https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch?"
                "dbcode=CJZK&captchaToken=active"
            )
        ),
        OldSearchContractPage(
            url=(
                "https://webvpn.hhu.edu.cn/https/cnki/kns/advsearch?"
                "dbcode=CJZK&verifyToken=active"
            )
        ),
    ],
    ids=(
        "verification-title",
        "missing-grade-tag",
        "missing-major-tag",
        "puzzle-prompt",
        "verification-path",
        "captcha-type",
        "captcha-token",
        "verify-token",
    ),
)
def test_status_keeps_captcha_when_old_search_contract_is_not_met(
    monkeypatch: pytest.MonkeyPatch,
    page: OldSearchContractPage,
) -> None:
    monkeypatch.setattr(
        session_module,
        "classify_public_state",
        lambda **_kwargs: SessionStatus.CAPTCHA,
    )
    session = CnkiSession()
    session.page = page

    assert session.status() is SessionStatus.CAPTCHA


@pytest.mark.parametrize(
    "public_status",
    [
        SessionStatus.RATE_LIMITED,
        SessionStatus.PERMISSION_DENIED,
        SessionStatus.LOGIN_REQUIRED,
        SessionStatus.SESSION_EXPIRED,
    ],
)
def test_status_does_not_override_non_captcha_states(
    monkeypatch: pytest.MonkeyPatch,
    public_status: SessionStatus,
) -> None:
    monkeypatch.setattr(
        session_module,
        "classify_public_state",
        lambda **_kwargs: public_status,
    )
    session = CnkiSession()
    session.page = OldSearchContractPage()

    assert session.status() is public_status


def test_status_keeps_captcha_when_old_search_locator_is_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        session_module,
        "classify_public_state",
        lambda **_kwargs: SessionStatus.CAPTCHA,
    )
    session = CnkiSession()
    session.page = OldSearchContractPage(locator_error=RuntimeError("page closed"))

    assert session.status() is SessionStatus.CAPTCHA


@pytest.mark.parametrize("ordinary_number", ["429", "403"])
def test_ready_cnki_page_does_not_treat_bare_numbers_as_http_errors(
    ordinary_number: str,
) -> None:
    status = classify_public_state(
        url="https://webvpn.hhu.edu.cn/https/cnki/",
        title="中国知网",
        visible_text=f"高级检索 期刊目录共 {ordinary_number} 种",
    )
    assert status is SessionStatus.READY
