import pytest

from cnki_search.models import SearchMode, SearchRequest, SessionStatus, ToolResponse


def test_tool_response_serializes_stable_shape() -> None:
    response = ToolResponse.success(SessionStatus.READY, {"count": 1})
    assert response.to_dict() == {
        "ok": True,
        "status": "ready",
        "message": "",
        "data": {"count": 1},
        "warnings": [],
        "next_action": None,
    }


def test_search_request_rejects_more_than_three_pages() -> None:
    with pytest.raises(ValueError, match="1 到 3"):
        SearchRequest(mode=SearchMode.ADVANCED, query="创新", pages=4)


def test_all_required_session_statuses_are_present() -> None:
    assert {item.value for item in SessionStatus} == {
        "login_required",
        "waiting_for_user",
        "ready",
        "captcha",
        "permission_denied",
        "rate_limited",
        "session_expired",
        "closed",
    }
