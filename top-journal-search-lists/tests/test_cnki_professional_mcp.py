import asyncio

import pytest

from cnki_search import mcp_server
from cnki_search.mcp_server import CnkiMcpServer


class RecordingMcp:
    def __init__(self, _name: str) -> None:
        self.tools: dict[str, dict] = {}
        self._mcp_server = type("LowLevel", (), {"version": None})()

    def tool(self, *, name: str, description: str = ""):
        def register(fn):
            self.tools[name] = {"fn": fn, "description": description}
            return fn
        return register


class FakeProfessionalService:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    async def search_group(self, topic, group, *, limit, year_from, year_to):
        self.calls.append((topic, group, limit, year_from, year_to))
        return {"ok": True, "mode": "webvpn", "status": "success",
                "human_intervention_required": False, "records": []}


def _server_with_service(service: FakeProfessionalService) -> CnkiMcpServer:
    async def factory():
        return service
    return CnkiMcpServer(professional_factory=factory)


def test_both_tools_are_registered() -> None:
    assert mcp_server.REQUIRED_TOOLS == ["cnki_search", "cnki_professional_search"]
    mcp = CnkiMcpServer().build_fastmcp(RecordingMcp)
    assert set(mcp.tools) == {"cnki_search", "cnki_professional_search"}


def test_tool_description_states_the_human_attendance_requirement() -> None:
    """描述里必须写明约束，否则调用方会把它当成可随手调用的能力。"""
    mcp = CnkiMcpServer().build_fastmcp(RecordingMcp)
    description = mcp.tools["cnki_professional_search"]["description"]
    for statement in ("本人登录", "不可用于定时任务", "CNKI_WEBVPN_HOME"):
        assert statement in description


def test_disabled_webvpn_returns_configuration_error_without_launching_anything(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """未启用时绝不能擅自打开浏览器窗口要求登录。"""
    monkeypatch.delenv(mcp_server.WEBVPN_HOME_ENV, raising=False)
    server = CnkiMcpServer()
    result = asyncio.run(server.cnki_professional_search("数字经济"))
    assert result["ok"] is False
    assert result["status"] == "configuration_error"
    assert mcp_server.WEBVPN_HOME_ENV in result["detail"]
    assert server._professional is None


def test_enabled_flag_follows_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(mcp_server.WEBVPN_HOME_ENV, raising=False)
    assert mcp_server.webvpn_enabled() is False
    monkeypatch.setenv(mcp_server.WEBVPN_HOME_ENV, "   ")
    assert mcp_server.webvpn_enabled() is False      # 空白不算配置
    monkeypatch.setenv(mcp_server.WEBVPN_HOME_ENV, "https://webvpn.example.edu.cn/https/abc/")
    assert mcp_server.webvpn_enabled() is True


def test_english_priority_groups_are_refused_before_any_session_is_opened() -> None:
    service = FakeProfessionalService()
    server = _server_with_service(service)
    result = asyncio.run(server.cnki_professional_search("主题", "ssci"))
    assert result["status"] == "configuration_error"
    assert "ai4scholar" in result["detail"]
    assert service.calls == []          # 未触及会话，未消耗限流预算


def test_arguments_are_passed_through_to_the_service() -> None:
    service = FakeProfessionalService()
    server = _server_with_service(service)
    asyncio.run(server.cnki_professional_search(
        "数字经济", "cssci", 15, 2020, 2026))
    assert service.calls == [("数字经济", "cssci", 15, 2020, 2026)]


def test_session_is_created_once_and_reused() -> None:
    """票据不能跨进程复用，会话必须在同一进程内保持存活。"""
    service = FakeProfessionalService()
    created = 0

    async def factory():
        nonlocal created
        created += 1
        return service

    server = CnkiMcpServer(professional_factory=factory)
    asyncio.run(server.cnki_professional_search("主题一"))
    asyncio.run(server.cnki_professional_search("主题二"))
    assert created == 1 and len(service.calls) == 2


def test_limit_bounds_stay_at_twenty_until_page_size_is_confirmed() -> None:
    """P3（每页可否设为 50）未确认前不得声称支持 50。

    声称 50 却只返回 20，调用方会误以为结果被截断，进而重复检索——既浪费
    限流预算，也可能把「就这么多文献」的错误结论写进综述。
    """
    import inspect

    assert mcp_server.MAX_LIMIT == 20
    mcp = CnkiMcpServer().build_fastmcp(RecordingMcp)
    for name in ("cnki_search", "cnki_professional_search"):
        parameters = inspect.signature(mcp.tools[name]["fn"]).parameters
        assert parameters["limit"].default == 20, name


def test_shutdown_still_rejects_professional_calls() -> None:
    server = _server_with_service(FakeProfessionalService())
    server.shutdown()
    with pytest.raises(RuntimeError):
        asyncio.run(server.cnki_professional_search("主题"))
