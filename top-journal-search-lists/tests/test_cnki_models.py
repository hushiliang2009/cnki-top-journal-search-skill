from dataclasses import fields

import pytest

from cnki_search.models import PaperRecord, SearchOutcome, SearchRequest, SearchStatus


def test_request_accepts_only_nonempty_theme_and_limit_1_to_20() -> None:
    assert SearchRequest("数字化转型", 20).query == "数字化转型"
    assert SearchRequest("  ＡＢＣ　主题  ").query == "ABC 主题"
    assert SearchRequest("主题").limit == 20
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


def _record(*, title: str = "示例论文", journal: str = "经济研究", year: int | None = 2026) -> PaperRecord:
    return PaperRecord(
        title=title,
        authors=[],
        journal_raw=journal,
        publication_date=str(year or ""),
        publication_year=year,
        document_type="期刊",
        citations=None,
        downloads=None,
        is_online_first=False,
        result_rank=1,
        source_database="CNKI",
        search_query="主题",
    )


@pytest.mark.parametrize(
    "record",
    [_record(title=""), _record(journal=""), _record(year=None)],
)
def test_outcome_rejects_incomplete_records_in_formal_records(record: PaperRecord) -> None:
    with pytest.raises(ValueError, match="正式题录"):
        SearchOutcome(SearchStatus.SUCCESS, "主题", [record], [], 0, [], "2026-07-22T00:00:00+00:00")


def test_outcome_accepts_incomplete_records_only_in_incomplete_collection() -> None:
    incomplete = _record(year=None)
    outcome = SearchOutcome(
        SearchStatus.PARTIAL,
        "主题",
        [],
        [incomplete],
        0,
        [],
        "2026-07-22T00:00:00+00:00",
    )
    assert outcome.incomplete_records == [incomplete]


def test_catalog_version_is_fixed_and_not_a_constructor_argument() -> None:
    assert _record().catalog_version == "2026-07-15"
    with pytest.raises(TypeError):
        PaperRecord(
            title="示例论文", authors=[], journal_raw="经济研究", publication_date="2026",
            publication_year=2026, document_type="期刊", citations=None, downloads=None,
            is_online_first=False, result_rank=1, source_database="CNKI", search_query="主题",
            catalog_version="other-version",
        )


@pytest.mark.parametrize("year", [1899, 2100])
def test_outcome_rejects_formal_records_with_unverifiable_year(year: int) -> None:
    with pytest.raises(ValueError, match="发表年度"):
        SearchOutcome(
            SearchStatus.SUCCESS,
            "主题",
            [_record(year=year)],
            [],
            0,
            [],
            "2026-07-22T00:00:00+00:00",
        )


def test_invalid_arguments_return_structured_status_not_raw_error() -> None:
    """参数校验应走结构化状态，否则调用方拿不到 status 也拿不到 warnings。"""
    from pathlib import Path

    from cnki_search.models import SearchStatus
    from cnki_search.service import CnkiPublicSearchService

    catalog = Path(__file__).resolve().parents[1] / "references" / "Academic_Journal_Master_Directory_20260715.md"
    service = CnkiPublicSearchService(catalog=catalog)
    for query, limit in (("   ", 20), ("主题", 0), ("主题", 21)):
        outcome = service.search(query, limit)
        assert outcome.status is SearchStatus.PAGE_CONTRACT_CHANGED
        assert outcome.warnings and outcome.records == []
