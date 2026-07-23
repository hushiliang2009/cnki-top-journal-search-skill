from pathlib import Path
from datetime import date

import pytest

from cnki_search import results
from cnki_search.search import PageContractChanged


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
    html = (fixtures / "public_results.html").read_text(encoding="utf-8")
    assert "href=" in html
    payload = results.parse_public_result_page(
        html,
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
        ("发布时间：2026-07-20 10:20:30，已核验", 2026),
        ("出版时间 2026/07/20，附注", 2026),
        ("2026-13-40", None),
        ("2026-07-20 24:00", None),
        ("2026年07月", None),
        ("1899", None),
        ("2100", None),
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


def test_visible_result_markers_without_public_table_stop_on_contract_change() -> None:
    with pytest.raises(PageContractChanged, match="结果表"):
        results.parse_public_result_page("<main>题名 作者 来源 日期 数据库</main>", query="主题", limit=20)


def test_future_year_beyond_shared_range_is_incomplete() -> None:
    year = date.today().year + 2
    html = (
        "<table class='result-table-list'><tr>"
        "<td class='seq'>1</td><td class='name'><a>题录</a></td>"
        "<td class='source'><a>期刊</a></td><td class='date'>"
        f"{year}</td><td class='data'>期刊</td></tr></table>"
    )
    parsed = results.parse_public_result_page(html, query="主题", limit=20)
    assert parsed.records == []
    assert [item.publication_year for item in parsed.incomplete_records] == [year]


def test_public_result_parser_preserves_outer_rows_and_bibliographic_fields(fixtures: Path) -> None:
    parsed = results.parse_public_result_page(
        (fixtures / "public_results_parser_edge_cases.html").read_text(encoding="utf-8"),
        query="主题",
        limit=20,
    )
    assert parsed.total_rows == 3
    assert [record.title for record in parsed.records] == [
        "Digital Transformation Study", "Incomplete Tags Keep This Title", "Slash Date Record",
    ]
    assert parsed.records[0].authors == ["Alice Adams", "Bob Brown"]
    assert parsed.records[1].authors == ["Carol Chen", "David Du"]
    assert [record.publication_year for record in parsed.records] == [2026, 2025, 2024]
    assert (parsed.records[0].citations, parsed.records[0].downloads) == (1234, 5678)
    assert (parsed.records[1].citations, parsed.records[1].downloads) == (9876, 4321)


def test_found_result_table_without_bibliographic_rows_stops_on_contract_change() -> None:
    html = "<table class='result-table-list'><thead><tr><th>题名</th></tr></thead></table>"
    with pytest.raises(PageContractChanged, match="题录"):
        results.parse_public_result_page(html, query="主题", limit=20)
