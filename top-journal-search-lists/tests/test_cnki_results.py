from pathlib import Path

import pytest

from cnki_search import results


def test_public_result_requires_title_journal_and_valid_year(fixtures: Path) -> None:
    parsed = results.parse_public_result_page(
        (fixtures / "public_results.html").read_text(encoding="utf-8"),
        query="数字化转型",
        limit=20,
    )
    assert len(parsed.records) == 1
    record = parsed.records[0]
    assert (record.title, record.journal_raw, record.publication_year) == (
        "数字化转型与企业创新", "经济研究", 2026,
    )
    assert record.document_type == "期刊"
    assert (record.citations, record.downloads, record.is_online_first) == (12, 108, True)
    assert parsed.excluded_non_journal_rows == 1


def test_incomplete_rows_never_enter_formal_records(fixtures: Path) -> None:
    parsed = results.parse_public_result_page(
        (fixtures / "public_incomplete_results.html").read_text(encoding="utf-8"),
        query="主题",
        limit=20,
    )
    assert parsed.records == []
    assert len(parsed.incomplete_records) == 3


def test_public_record_serialization_contains_no_url_fields(fixtures: Path) -> None:
    payload = results.parse_public_result_page(
        (fixtures / "public_results.html").read_text(encoding="utf-8"),
        query="主题",
        limit=20,
    ).records[0].to_dict()
    assert not any("url" in key.casefold() for key in payload)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026", 2026),
        ("2026-07", 2026),
        ("2026-07-20 10:20", 2026),
        ("2026-13-40", None),
        ("2026-07-20 24:00", None),
        ("2026年07月", None),
    ],
)
def test_publication_year_requires_a_valid_iso_date(value: str, expected: int | None) -> None:
    assert results.extract_publication_year(value) == expected


def test_no_results_page_contains_no_records(fixtures: Path) -> None:
    parsed = results.parse_public_result_page(
        (fixtures / "public_no_results.html").read_text(encoding="utf-8"),
        query="主题",
        limit=20,
    )
    assert parsed.records == []
    assert parsed.incomplete_records == []
    assert parsed.total_rows == 0
