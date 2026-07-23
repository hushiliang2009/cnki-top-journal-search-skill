import inspect

from cnki_search.mcp_server import CnkiMcpServer, REQUIRED_TOOLS
from cnki_search.models import SearchOutcome, SearchStatus


class FakeService:
    def search(self, query: str, limit: int = 20) -> SearchOutcome:
        return SearchOutcome(
            SearchStatus.NO_RESULTS, query, [], [], 0, [], "2026-07-22T00:00:00+00:00",
        )


def test_mcp_exposes_exact_public_tool() -> None:
    server = CnkiMcpServer(service=FakeService())
    assert server.tool_names() == REQUIRED_TOOLS == ["cnki_search"]


def test_public_signature_is_query_and_limit_only() -> None:
    parameters = inspect.signature(CnkiMcpServer.cnki_search).parameters
    assert list(parameters) == ["self", "query", "limit"]
    assert parameters["limit"].default == 20


def test_removed_tools_are_not_attributes() -> None:
    server = CnkiMcpServer(service=FakeService())
    for name in (
        "cnki_status", "cnki_login", "cnki_fetch_details", "cnki_export",
        "cnki_download", "cnki_close_session",
    ):
        assert not hasattr(server, name)


def test_public_tool_returns_service_outcome() -> None:
    assert CnkiMcpServer(service=FakeService()).cnki_search("主题") == {
        "ok": True,
        "status": "no_results",
        "query": "主题",
        "records": [],
        "incomplete_records": [],
        "excluded_non_journal_rows": 0,
        "warnings": [],
        "searched_at": "2026-07-22T00:00:00+00:00",
    }


def test_tool_schema_declares_machine_enforceable_limit_range() -> None:
    """limit 的 1–20 此前只写在文档里，tools/list 的 schema 无任何约束。"""
    from mcp.server.fastmcp import FastMCP

    mcp = CnkiMcpServer(service=FakeService()).build_fastmcp(FastMCP)
    tool = next(item for item in mcp._tool_manager.list_tools() if item.name == "cnki_search")
    limit = tool.parameters["properties"]["limit"]
    assert (limit["minimum"], limit["maximum"], limit["default"]) == (1, 20, 20)


def test_server_announces_product_version_not_sdk_version() -> None:
    """serverInfo 此前通告 MCP SDK 版本（1.28.1），而非本工具版本。"""
    from mcp.server.fastmcp import FastMCP

    from cnki_search import __version__

    mcp = CnkiMcpServer(service=FakeService()).build_fastmcp(FastMCP)
    assert mcp._mcp_server.version == __version__ == "0.3.0"


def test_shutdown_does_not_block_on_queued_work() -> None:
    """原实现 submit 一个空任务并 .result() 等待，队列里排着限速检索时会被阻塞。"""
    server = CnkiMcpServer(service=FakeService())
    server.shutdown()
    server.shutdown()  # 幂等
    assert server._shutdown is True
