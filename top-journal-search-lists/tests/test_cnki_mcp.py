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
