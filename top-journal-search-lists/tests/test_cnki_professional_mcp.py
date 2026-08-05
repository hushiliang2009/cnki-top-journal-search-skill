import asyncio
from datetime import date

import pytest

from cnki_search import mcp_server
from cnki_search.browser import BrowserUnavailableError
from cnki_search.mcp_server import CnkiMcpServer
from cnki_search.search import PageContractChanged
from cnki_search.webvpn import (
    ExpressionTruncated,
    WebVpnLoginTimeout,
    WebVpnNavigationError,
    WebVpnWindowClosed,
)


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


def test_enabled_default_server_builds_production_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = FakeProfessionalService()
    created = 0

    async def build():
        nonlocal created
        created += 1
        return runtime

    monkeypatch.setenv(
        "CNKI_WEBVPN_HOME", "https://webvpn.example.edu.cn/https/abc/"
    )
    monkeypatch.setattr(
        mcp_server, "build_professional_runtime_from_env", build, raising=False
    )
    server = CnkiMcpServer()
    result = asyncio.run(server.cnki_professional_search("数字经济"))

    assert result["status"] == "success"
    assert created == 1


def test_concurrent_first_calls_build_and_close_exactly_one_runtime() -> None:
    async def scenario() -> None:
        factory_started = asyncio.Event()
        release_factory = asyncio.Event()
        runtimes = []

        class Runtime(FakeProfessionalService):
            def __init__(self) -> None:
                super().__init__()
                self.close_calls = 0

            async def aclose(self) -> None:
                self.close_calls += 1

        async def factory():
            runtime = Runtime()
            runtimes.append(runtime)
            factory_started.set()
            await release_factory.wait()
            return runtime

        server = CnkiMcpServer(professional_factory=factory)
        first = asyncio.create_task(
            server.cnki_professional_search("数字经济")
        )
        await factory_started.wait()
        second = asyncio.create_task(
            server.cnki_professional_search("共同富裕")
        )
        await asyncio.sleep(0)
        release_factory.set()

        results = await asyncio.gather(first, second)
        assert [item["status"] for item in results] == ["success", "success"]
        await server.aclose()

        assert len(runtimes) == 1
        assert runtimes[0].close_calls == 1

    asyncio.run(scenario())


def test_failed_factory_is_not_cached_and_next_call_can_retry() -> None:
    async def scenario() -> None:
        runtime = FakeProfessionalService()
        attempts = 0

        async def factory():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise BrowserUnavailableError("首次初始化失败")
            return runtime

        server = CnkiMcpServer(professional_factory=factory)
        first = await server.cnki_professional_search("数字经济")
        second = await server.cnki_professional_search("数字经济")

        assert first["status"] == "configuration_error"
        assert second["status"] == "success"
        assert attempts == 2
        assert server._professional is runtime

    asyncio.run(scenario())


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


def test_limit_matches_the_measured_page_size_ceiling() -> None:
    """上限 50 来自实测：结果页「显示」下拉档位为 10/20/50，选 50 确实返回 50 行。

    不能凭空往上写——声称支持的条数大于站点实际返回，调用方会误以为结果被
    截断而重复检索，既浪费限流预算，也可能把"就这么多文献"的错误结论写进综述。
    """
    import inspect

    # 两种模式的上限不同，且都必须反映各自真正能拿到的条数
    assert mcp_server.MAX_LIMIT == 20                  # 公开模式不切档位
    assert mcp_server.MAX_PROFESSIONAL_LIMIT == 50     # 专业检索主动切到 50
    mcp = CnkiMcpServer().build_fastmcp(RecordingMcp)
    expected = {"cnki_search": 20, "cnki_professional_search": 50}
    for name, default in expected.items():
        parameters = inspect.signature(mcp.tools[name]["fn"]).parameters
        assert parameters["limit"].default == default, name


def test_shutdown_still_rejects_professional_calls() -> None:
    server = _server_with_service(FakeProfessionalService())
    server.shutdown()
    with pytest.raises(RuntimeError):
        asyncio.run(server.cnki_professional_search("主题"))


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (BrowserUnavailableError("没有图形界面"), "configuration_error"),
        (ValueError("WebVPN 入口必须是 https 地址"), "configuration_error"),
        (WebVpnLoginTimeout("登录超时"), "login_required"),
        (WebVpnWindowClosed("窗口已关闭"), "login_required"),
        (WebVpnNavigationError("页面改版"), "page_contract_changed"),
        (ExpressionTruncated("表达式被截断"), "page_contract_changed"),
        (PageContractChanged("结果表结构变化"), "page_contract_changed"),
    ],
)
def test_runtime_errors_are_mapped_to_stable_mcp_statuses(
    error: Exception, expected_status: str
) -> None:
    class FailingRuntime:
        async def search_group(self, *_args, **_kwargs):
            raise error

    server = _server_with_service(FailingRuntime())
    result = asyncio.run(server.cnki_professional_search("数字经济"))

    assert result["ok"] is False
    assert result["status"] == expected_status
    assert result["detail"] == str(error)


def test_professional_cancellation_propagates() -> None:
    class CancelledRuntime:
        async def search_group(self, *_args, **_kwargs):
            raise asyncio.CancelledError

    server = _server_with_service(CancelledRuntime())
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(server.cnki_professional_search("数字经济"))


def test_professional_year_schema_has_supported_bounds() -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = CnkiMcpServer().build_fastmcp(FastMCP)
    tool = next(
        item
        for item in mcp._tool_manager.list_tools()
        if item.name == "cnki_professional_search"
    )
    for name in ("year_from", "year_to"):
        integer_schema = tool.parameters["properties"][name]["anyOf"][0]
        assert integer_schema["minimum"] == 1900
        assert integer_schema["maximum"] == date.today().year + 1


def _professional_tool_schema() -> dict:
    from mcp.server.fastmcp import FastMCP

    mcp = CnkiMcpServer().build_fastmcp(FastMCP)
    tool = next(
        item
        for item in mcp._tool_manager.list_tools()
        if item.name == "cnki_professional_search"
    )
    return tool.parameters


def test_group_schema_lists_exactly_the_controlled_scopes() -> None:
    assert _professional_tool_schema()["properties"]["group"]["pattern"] == (
        "^(chinese_top_journals|cssci)$"
    )


def test_facet_and_field_are_never_caller_controlled() -> None:
    """来源类别和检索字段是内部策略，暴露成入参就等于让调用方绕过目录资格。"""
    properties = _professional_tool_schema()["properties"]
    for forbidden in ("source_category", "source_category_code", "topic_field"):
        assert forbidden not in properties


@pytest.mark.parametrize("group", list(("chinese_top_journals", "cssci")))
def test_every_controlled_group_reaches_the_service(group: str) -> None:
    service = FakeProfessionalService()
    server = _server_with_service(service)

    asyncio.run(server.cnki_professional_search("环境政策", group))

    assert [call[1] for call in service.calls] == [group]
