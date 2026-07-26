import asyncio
import inspect
import os
import subprocess
import sys
from pathlib import Path

import pytest

from cnki_search_env.mcp_server import CnkiMcpServer, REQUIRED_TOOLS
from cnki_search_env.models import SearchOutcome, SearchStatus


class FakeService:
    async def search(self, query: str, limit: int = 20) -> SearchOutcome:
        return SearchOutcome(
            SearchStatus.NO_RESULTS, query, [], [], 0, [], "2026-07-22T00:00:00+00:00",
        )


def test_mcp_exposes_exact_public_tool() -> None:
    server = CnkiMcpServer(service=FakeService())
    assert server.tool_names() == REQUIRED_TOOLS == ["cnki_search_env"]


def test_public_signature_is_query_and_limit_only() -> None:
    parameters = inspect.signature(CnkiMcpServer.cnki_search_env).parameters
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
    assert asyncio.run(CnkiMcpServer(service=FakeService()).cnki_search_env("主题")) == {
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
    tool = next(item for item in mcp._tool_manager.list_tools() if item.name == "cnki_search_env")
    limit = tool.parameters["properties"]["limit"]
    query = tool.parameters["properties"]["query"]
    assert (limit["minimum"], limit["maximum"], limit["default"]) == (1, 20, 20)
    assert query["minLength"] == 1


def test_fastmcp_rejects_blank_query_before_service_and_returns_structured_valid_outcome() -> None:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError

    mcp = CnkiMcpServer(service=FakeService()).build_fastmcp(FastMCP)
    tool = next(item for item in mcp._tool_manager.list_tools() if item.name == "cnki_search_env")
    valid = asyncio.run(tool.run({"query": "topic"}))
    assert valid["status"] == "no_results" and valid["query"] == "topic"
    with pytest.raises(ToolError):
        asyncio.run(tool.run({"query": "   "}))
    for limit in (0, 21):
        with pytest.raises(ToolError):
            asyncio.run(tool.run({"query": "topic", "limit": limit}))


def test_stage4a_schema_query_and_cache_behave_independently_in_both_layouts() -> None:
    roots = (Path(__file__).resolve().parents[1] / "scripts", Path(__file__).resolve().parents[1] / "mcpb" / "src")
    program = """
import asyncio
from cnki_search_env.cache import SearchCache
from cnki_search_env.mcp_server import CnkiMcpServer
from cnki_search_env.models import SearchOutcome, SearchRequest, SearchStatus
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

class Service:
    async def search(self, query, limit=20):
        return SearchOutcome(SearchStatus.NO_RESULTS, query, [], [], 0, [], 'now')

assert SearchRequest('  ＡＢＣ　topic  ').query == 'ABC topic'
cache = SearchCache()
cache.put('ABC topic', 20, SearchOutcome(SearchStatus.SUCCESS, 'ABC topic', [], [], 0, [], 'now'))
assert cache.get('abc topic', 20) is not None
tool = next(item for item in CnkiMcpServer(Service()).build_fastmcp(FastMCP)._tool_manager.list_tools() if item.name == 'cnki_search_env')
assert tool.parameters['properties']['query']['minLength'] == 1
assert asyncio.run(tool.run({'query': 'topic'}))['status'] == 'no_results'
try:
    asyncio.run(tool.run({'query': '   '}))
except ToolError:
    pass
else:
    raise AssertionError('blank query was accepted')
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


def test_server_announces_product_version_not_sdk_version() -> None:
    """serverInfo 此前通告 MCP SDK 版本（1.28.1），而非本工具版本。"""
    from mcp.server.fastmcp import FastMCP

    from cnki_search_env import __version__

    mcp = CnkiMcpServer(service=FakeService()).build_fastmcp(FastMCP)
    assert mcp._mcp_server.version == __version__ == "0.1.0"


def test_shutdown_does_not_block_on_queued_work() -> None:
    """原实现 submit 一个空任务并 .result() 等待，队列里排着限速检索时会被阻塞。"""
    server = CnkiMcpServer(service=FakeService())
    server.shutdown()
    server.shutdown()  # 幂等
    assert server._shutdown is True
