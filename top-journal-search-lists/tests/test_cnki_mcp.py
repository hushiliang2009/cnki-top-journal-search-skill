import inspect
import hashlib
from pathlib import Path

import pytest

from cnki_search.mcp_server import CnkiMcpServer, REQUIRED_TOOLS
from cnki_search.models import PaperRecord, SessionStatus
from cnki_search.session import DIRECT_CNKI_SEARCH_URL


def test_mcp_exposes_exact_tool_set() -> None:
    server = CnkiMcpServer()
    assert set(server.tool_names()) == set(REQUIRED_TOOLS) == {
        "cnki_status",
        "cnki_login",
        "cnki_search",
        "cnki_fetch_details",
        "cnki_export",
        "cnki_download",
        "cnki_close_session",
    }


def test_search_public_signature_has_no_entry_version_parameter() -> None:
    parameters = inspect.signature(CnkiMcpServer.cnki_search).parameters
    assert list(parameters) == ["self", "query", "mode", "pages", "fields", "filters"]


def test_status_does_not_open_browser_and_has_stable_shape() -> None:
    server = CnkiMcpServer()
    response = server.cnki_status()
    assert set(response) == {"ok", "status", "message", "data", "warnings", "next_action"}
    assert response["status"] == SessionStatus.LOGIN_REQUIRED.value
    assert server.session.page is None


def test_close_clears_session_resources() -> None:
    server = CnkiMcpServer()
    response = server.cnki_close_session()
    assert response["status"] == "closed"
    assert server.session.page is None
    assert server.session.browser is None


def test_build_fastmcp_is_lazy_when_sdk_is_unavailable(monkeypatch) -> None:
    server = CnkiMcpServer()
    registered: list[str] = []

    class FakeFastMCP:
        def __init__(self, _name: str) -> None:
            pass

        def tool(self, *, name: str, description: str):
            assert description
            registered.append(name)
            return lambda function: function

    mcp = server.build_fastmcp(FakeFastMCP)
    assert mcp is not None
    assert registered == REQUIRED_TOOLS


class FakeBody:
    def inner_text(self, timeout: int) -> str:
        assert timeout == 5_000
        return "中国知网 文献详情"


class FakeDetailPage:
    url = "https://webvpn.hhu.edu.cn/kns/detail"

    def title(self) -> str:
        return "文献详情-中国知网"

    def locator(self, selector: str) -> FakeBody:
        assert selector == "body"
        return FakeBody()

    def content(self) -> str:
        return (Path(__file__).with_name("fixtures") / "detail.html").read_text(
            encoding="utf-8"
        )

    def close(self) -> None:
        pass


class FakeResultPage:
    def goto(self, _url: str, **_kwargs) -> None:
        raise AssertionError("详情不得直接 goto")


class FakeReadySession:
    def __init__(self) -> None:
        self.page = FakeResultPage()

    def status(self) -> SessionStatus:
        return SessionStatus.READY


class AccessDeniedSession:
    @property
    def page(self):
        raise AssertionError("权限确认缺失时不得访问会话或驱动")

    def status(self) -> SessionStatus:
        raise AssertionError("权限确认缺失时不得访问会话")


class FakeMcpDownloadDriver:
    def __init__(self, _page) -> None:
        pass

    def download_selected(self, selected_index: int, target: Path) -> Path:
        target.write_bytes(b"%PDF-1.7 test")
        return target


def test_mcp_download_requires_access_confirmation_before_session_access() -> None:
    server = CnkiMcpServer(session=AccessDeniedSession())

    response = server.cnki_download([1], "not-created", access_confirmed=False)

    assert response["ok"] is False
    assert response["status"] == SessionStatus.PERMISSION_DENIED.value
    assert "访问权限" in response["message"]


def test_mcp_download_reports_path_size_and_sha256(monkeypatch, skill_root: Path) -> None:
    monkeypatch.setattr("cnki_search.mcp_server.PlaywrightDownloadDriver", FakeMcpDownloadDriver)
    server = CnkiMcpServer(session=FakeReadySession())
    server.records = [PaperRecord(title="下载测试")]
    target = skill_root / "tests" / "_mcp_download_metadata_test"
    target.mkdir(exist_ok=True)

    try:
        response = server.cnki_download([1], str(target), access_confirmed=True)

        assert response["ok"] is True
        assert response["data"] == [{
            "path": str(target / "下载测试.pdf"),
            "size_bytes": len(b"%PDF-1.7 test"),
            "sha256": hashlib.sha256(b"%PDF-1.7 test").hexdigest(),
        }]
    finally:
        for path in target.iterdir():
            path.unlink()
        target.rmdir()


class FakeNavigator:
    def __init__(self) -> None:
        self.calls: list[int] = []

    def open_selected(self, _page, selected_index: int) -> FakeDetailPage:
        self.calls.append(selected_index)
        return FakeDetailPage()


class FakeSearchPage:
    url = DIRECT_CNKI_SEARCH_URL

    def wait_for_load_state(self, state: str) -> None:
        assert state == "domcontentloaded"

    def content(self) -> str:
        return "<html><body></body></html>"


class FakeSearchSession:
    def __init__(self, open_status: SessionStatus) -> None:
        self.page = FakeSearchPage()
        self.open_status = open_status
        self.open_search_calls = 0

    def status(self) -> SessionStatus:
        return SessionStatus.READY

    def open_search(self) -> SessionStatus:
        self.open_search_calls += 1
        return self.open_status


def test_search_opens_new_page_before_runner(monkeypatch) -> None:
    session = FakeSearchSession(SessionStatus.READY)
    calls: list[str] = []

    class FakeDriver:
        def __init__(self, _page) -> None:
            pass

        def assert_new_search_page(self) -> None:
            calls.append("contract")

    monkeypatch.setattr("cnki_search.mcp_server.PlaywrightPageDriver", FakeDriver)
    monkeypatch.setattr(
        "cnki_search.mcp_server.AdvancedSearchRunner.run",
        lambda _self, _driver, _request: calls.append("runner"),
    )
    monkeypatch.setattr("cnki_search.mcp_server.parse_result_page", lambda *_a, **_k: [])
    server = CnkiMcpServer(session=session)
    response = server.cnki_search("数字化转型")
    assert response["ok"] is True
    assert response["status"] == SessionStatus.READY.value
    assert session.open_search_calls == 1
    assert calls == ["contract", "runner"]


@pytest.mark.parametrize(
    "status",
    [
        SessionStatus.CAPTCHA,
        SessionStatus.RATE_LIMITED,
        SessionStatus.PERMISSION_DENIED,
        SessionStatus.SESSION_EXPIRED,
    ],
)
def test_search_stops_when_new_page_is_not_ready(status: SessionStatus) -> None:
    session = FakeSearchSession(status)
    server = CnkiMcpServer(session=session)
    response = server.cnki_search("数字化转型")
    assert response["ok"] is False
    assert response["status"] == status.value
    assert session.open_search_calls == 1


class StatusChangingSearchPage:
    url = DIRECT_CNKI_SEARCH_URL

    def __init__(self) -> None:
        self.waits: list[str] = []
        self.content_calls = 0
        self.next_page_clicks = 0

    def wait_for_load_state(self, state: str) -> None:
        self.waits.append(state)

    def content(self) -> str:
        self.content_calls += 1
        return "<html><body></body></html>"

    def get_by_text(self, text: str, *, exact: bool):
        assert text == "下一页"
        assert exact is True
        return self

    def click(self) -> None:
        self.next_page_clicks += 1


class StatusChangingSearchSession:
    def __init__(self, statuses: list[SessionStatus]) -> None:
        self.page = StatusChangingSearchPage()
        self.statuses = statuses
        self.status_calls = 0

    def status(self) -> SessionStatus:
        status = self.statuses[self.status_calls]
        self.status_calls += 1
        return status

    def open_search(self) -> SessionStatus:
        return SessionStatus.READY


def test_search_stops_before_parsing_when_first_result_page_shows_captcha(monkeypatch) -> None:
    session = StatusChangingSearchSession([SessionStatus.READY, SessionStatus.CAPTCHA])

    class FakeDriver:
        def __init__(self, _page) -> None:
            pass

        def assert_new_search_page(self) -> None:
            pass

    monkeypatch.setattr("cnki_search.mcp_server.PlaywrightPageDriver", FakeDriver)
    monkeypatch.setattr("cnki_search.mcp_server.AdvancedSearchRunner.run", lambda *_a: None)
    response = CnkiMcpServer(session=session).cnki_search("query")
    assert response["ok"] is False
    assert response["status"] == SessionStatus.CAPTCHA.value
    assert response["next_action"] == "请在可见浏览器中手工完成登录或验证。"
    assert session.page.content_calls == 0
    assert session.page.next_page_clicks == 0


def test_search_stops_before_parsing_or_advancing_after_page_captcha(monkeypatch) -> None:
    session = StatusChangingSearchSession(
        [SessionStatus.READY, SessionStatus.READY, SessionStatus.CAPTCHA]
    )

    class FakeDriver:
        def __init__(self, _page) -> None:
            pass

        def assert_new_search_page(self) -> None:
            pass

    monkeypatch.setattr("cnki_search.mcp_server.PlaywrightPageDriver", FakeDriver)
    monkeypatch.setattr("cnki_search.mcp_server.AdvancedSearchRunner.run", lambda *_a: None)
    response = CnkiMcpServer(session=session).cnki_search("query", pages=3)
    assert response["ok"] is False
    assert response["status"] == SessionStatus.CAPTCHA.value
    assert response["next_action"] == "请在可见浏览器中手工完成登录或验证。"
    assert session.page.content_calls == 1
    assert session.page.next_page_clicks == 1


def test_fetch_details_uses_official_result_link_navigator() -> None:
    navigator = FakeNavigator()
    server = CnkiMcpServer(session=FakeReadySession(), detail_navigator=navigator)
    server.records = [PaperRecord(title="论文一", detail_url="https://kns.cnki.net/direct")]
    response = server.cnki_fetch_details([1])
    assert response["ok"] is True
    assert navigator.calls == [1]
    assert response["data"][0]["title"] == "数字化转型何以赋能探索式创新"
    assert response["data"][0]["abstract"] == "数字化转型促进探索式创新。"
    assert server.records[0].authors == ["方鑫", "陆亮亮", "唐秋雨", "谢佩洪"]
