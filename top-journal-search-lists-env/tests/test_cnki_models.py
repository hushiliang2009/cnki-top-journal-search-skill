from dataclasses import fields
from pathlib import Path
import asyncio

import pytest

from cnki_search_env.models import PaperRecord, SearchOutcome, SearchRequest, SearchStatus


def test_request_accepts_only_nonempty_theme_and_limit_1_to_20() -> None:
    assert SearchRequest("topic", 20).query == "topic"
    assert SearchRequest("  ＡＢＣ　topic  ").query == "ABC topic"
    assert SearchRequest("topic").limit == 20
    for query, limit in (("", 20), ("   ", 20), ("topic", 0), ("topic", 21)):
        with pytest.raises(ValueError):
            SearchRequest(query, limit)


def test_record_contract_has_no_url_or_fulltext_fields() -> None:
    names = {item.name for item in fields(PaperRecord)}
    assert {"title", "journal_raw", "publication_year", "priority_level"} <= names
    assert not names & {
        "detail_url", "download_url", "pdf_url", "caj_url", "doi",
        "abstract", "keywords", "affiliations", "download_status",
    }


def test_record_exposes_safe_dedup_and_match_metadata() -> None:
    names = {item.name for item in fields(PaperRecord)}
    assert {
        "topic_match_field",
        "matched_topic_fields",
        "matched_search_groups",
    } <= names
    assert not names & {
        "doi", "detail_url", "download_url", "pdf_url", "caj_url", "abstract"
    }


def test_search_statuses_match_public_contract() -> None:
    assert {item.value for item in SearchStatus} == {
        "success", "no_results", "partial", "rate_limited",
        "challenge_detected", "login_required", "forbidden",
        "page_contract_changed", "network_error", "configuration_error",
        # 知网「暂无数据，请稍后重试」——服务端临时拒绝，与无结果、安全验证
        # 都不同，补救办法是缩小分批
        "no_data_retry_later",
    }


def test_page_size_ceiling_is_declared_without_widening_public_search() -> None:
    """专业检索按每页 50 条取数；公开检索不切档位，上限仍为 20。"""
    from cnki_search_env.models import MAX_RESULTS_PER_PAGE, SearchRequest

    assert MAX_RESULTS_PER_PAGE == 50
    assert SearchRequest("topic", 20).limit == 20
    for bad in (0, 21):
        with pytest.raises(ValueError):
            SearchRequest("topic", bad)


def _record(*, title: str = "Example paper", journal: str = "Journal", year: int | None = 2026) -> PaperRecord:
    return PaperRecord(
        title=title,
        authors=[],
        journal_raw=journal,
        publication_date=str(year or ""),
        publication_year=year,
        document_type="journal",
        citations=None,
        downloads=None,
        is_online_first=False,
        result_rank=1,
        source_database="CNKI",
        search_query="topic",
    )


@pytest.mark.parametrize("record", [_record(title=""), _record(journal=""), _record(year=None)])
def test_outcome_rejects_incomplete_records_in_formal_records(record: PaperRecord) -> None:
    with pytest.raises(ValueError):
        SearchOutcome(SearchStatus.SUCCESS, "topic", [record], [], 0, [], "now")


def test_outcome_accepts_incomplete_records_only_in_incomplete_collection() -> None:
    incomplete = _record(year=None)
    outcome = SearchOutcome(SearchStatus.PARTIAL, "topic", [], [incomplete], 0, [], "now")
    assert outcome.incomplete_records == [incomplete]


def test_catalog_version_and_v4_metadata_are_fixed_and_not_constructor_arguments() -> None:
    record = _record()
    assert record.catalog_version == "4.0"
    assert record.catalog_date == "2026-07-29"
    assert record.revision_date == "2026-07-31"
    assert record.journal_id is None
    assert record.aliases == []
    assert record.index_subject_categories == {}
    assert record.source_memberships == []
    with pytest.raises(TypeError):
        PaperRecord(
            title="Example", authors=[], journal_raw="Journal", publication_date="2026",
            publication_year=2026, document_type="journal", citations=None, downloads=None,
            is_online_first=False, result_rank=1, source_database="CNKI", search_query="topic",
            catalog_version="other-version",
        )


@pytest.mark.parametrize("year", [1899, 2100])
def test_outcome_rejects_formal_records_with_unverifiable_year(year: int) -> None:
    with pytest.raises(ValueError):
        SearchOutcome(SearchStatus.SUCCESS, "topic", [_record(year=year)], [], 0, [], "now")


def test_service_rejects_invalid_arguments_instead_of_faking_page_contract_change() -> None:
    from cnki_search_env.service import CnkiPublicSearchService

    catalog = Path(__file__).resolve().parents[1] / "references" / "environment_journal_catalog_v4.0.json"
    service = CnkiPublicSearchService(catalog=catalog)
    for query, limit in (("   ", 20), ("topic", 0), ("topic", 21)):
        with pytest.raises(ValueError):
            asyncio.run(service.search(query, limit))


def test_record_bibliographic_fields_remove_controls_and_truncate_untrusted_text() -> None:
    record = PaperRecord(
        title="A\x00\u200b" + "t" * 800,
        authors=["B\n\u200b" + "a" * 300],
        journal_raw="J\r\u200b" + "j" * 500,
        publication_date="2026",
        publication_year=2026,
        document_type="journal",
        citations=None,
        downloads=None,
        is_online_first=False,
        result_rank=1,
        source_database="CNKI",
        search_query="topic",
    )
    fields_to_check = record.title + record.journal_raw + record.authors[0]
    assert "\x00" not in fields_to_check and "\u200b" not in fields_to_check
    assert len(record.title) < 800 and len(record.journal_raw) < 500 and len(record.authors[0]) < 300
