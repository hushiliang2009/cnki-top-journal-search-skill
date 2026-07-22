from dataclasses import fields

import pytest

from cnki_search.models import PaperRecord, SearchOutcome, SearchRequest, SearchStatus


def test_request_accepts_only_nonempty_theme_and_limit_1_to_20() -> None:
    assert SearchRequest("数字化转型", 20).query == "数字化转型"
    for query, limit in (("", 20), ("   ", 20), ("主题", 0), ("主题", 21)):
        with pytest.raises(ValueError):
            SearchRequest(query, limit)


def test_record_contract_has_no_url_or_fulltext_fields() -> None:
    names = {item.name for item in fields(PaperRecord)}
    assert {"title", "journal_raw", "publication_year", "priority_level"} <= names
    assert not names & {
        "detail_url", "download_url", "pdf_url", "caj_url", "doi",
        "abstract", "keywords", "affiliations", "download_status",
    }


def test_search_statuses_match_public_contract() -> None:
    assert {item.value for item in SearchStatus} == {
        "success", "no_results", "partial", "rate_limited",
        "challenge_detected", "login_required", "forbidden",
        "page_contract_changed", "network_error",
    }
