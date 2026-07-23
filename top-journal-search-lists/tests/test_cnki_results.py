from pathlib import Path
from datetime import date
import os
import subprocess
import sys

import pytest

from cnki_search import results
from cnki_search.search import PageContractChanged


def test_public_result_requires_title_journal_and_valid_year(fixtures: Path) -> None:
    parsed = results.parse_public_result_page(
        (fixtures / "public_results.html").read_text(encoding="utf-8"),
        query="数字化转型",
        limit=20,
    )
    assert len(parsed.records) == 2
    record = parsed.records[0]
    assert (record.title, record.journal_raw, record.publication_year) == (
        "数字化转型与企业创新", "经济研究", 2026,
    )
    assert record.document_type == "期刊"
    assert (record.citations, record.downloads, record.is_online_first) == (12, 108, True)
    assert record.authors == ["张三", "李四"]
    assert parsed.excluded_non_journal_rows == 1
    assert parsed.incomplete_records == []


def test_result_parsing_preserves_real_cnki_markup_fidelity(fixtures: Path) -> None:
    """<em> 高亮、多 <a> 作者、带秒时间戳、千分位——四种真实标记形态。"""
    parsed = results.parse_public_result_page(
        (fixtures / "public_results.html").read_text(encoding="utf-8"),
        query="供应链金融",
        limit=20,
    )
    record = parsed.records[1]
    # <em> 关键词高亮不得吞掉词间空格
    assert record.title == "Supply Chain Finance and Firm Innovation"
    # 每个 <a> 是一位作者，不得粘连成单个字符串
    assert record.authors == ["王五", "赵六", "孙七"]
    # 带秒时间戳曾使这条《管理世界》题录被整条丢弃
    assert (record.publication_date, record.publication_year) == ("2024-05-20 14:35:12", 2024)
    # 千分位分隔符曾使计数被判为缺失
    assert (record.citations, record.downloads) == (1024, 3204)


def test_nested_table_in_cell_does_not_swallow_following_records(fixtures: Path) -> None:
    """单元格内嵌套 <table> 的 </table> 曾提前结束结果表，丢光其后全部题录。"""
    parsed = results.parse_public_result_page(
        (fixtures / "public_results_nested_table.html").read_text(encoding="utf-8"),
        query="主题",
        limit=20,
    )
    assert parsed.total_rows == 2
    assert [record.title for record in parsed.records] == [
        "带脚注表格的题录", "嵌套表格之后的合法题录",
    ]


def test_stage3b_parser_behavior_runs_independently_in_both_layouts(fixtures: Path) -> None:
    fixture = fixtures / "public_results_stage3b.html"
    roots = (Path(__file__).resolve().parents[1] / "scripts", Path(__file__).resolve().parents[1] / "mcpb" / "src")
    program = f"""
from pathlib import Path
from cnki_search.results import parse_public_result_page

parsed = parse_public_result_page(Path({str(fixture)!r}).read_text(encoding='utf-8'), query='topic', limit=20)
assert parsed.total_rows == 2
assert [record.title for record in parsed.records] == ['Supply Chain Finance', 'After Nested Table']
assert parsed.records[0].authors == ['Alice Adams', 'Bob Brown']
assert parsed.records[0].publication_year == 2026
assert (parsed.records[0].citations, parsed.records[0].downloads) == (1234, 5678)
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


def test_date_candidate_rejects_malformed_suffixes_in_both_layouts() -> None:
    roots = (Path(__file__).resolve().parents[1] / "scripts", Path(__file__).resolve().parents[1] / "mcpb" / "src")
    program = """
from cnki_search.results import extract_publication_year

for value in (
    'bad 2026--01',
    'bad 2026/abc',
    'bad 2026 1:2',
    'first 2026--01 then 2024-05-01',
    'abc2026def',
    'version2026beta',
):
    assert extract_publication_year(value) is None, value
assert extract_publication_year('published 2026/07/20 10:20:30') == 2026
assert extract_publication_year('Published: 2026/07/20 10:20:30') == 2026
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


def test_missing_cell_close_is_completed_in_both_layouts(fixtures: Path) -> None:
    fixture = fixtures / "public_results_stage3b_missing_td.html"
    roots = (Path(__file__).resolve().parents[1] / "scripts", Path(__file__).resolve().parents[1] / "mcpb" / "src")
    program = f"""
from pathlib import Path
from cnki_search.results import parse_public_result_page

parsed = parse_public_result_page(Path({str(fixture)!r}).read_text(encoding='utf-8'), query='topic', limit=20)
assert [record.title for record in parsed.records] == ['Missing Cell Close']
assert parsed.incomplete_records == []
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


def test_missing_first_row_close_is_completed_in_both_layouts(fixtures: Path) -> None:
    fixture = fixtures / "public_results_stage3b_missing_tr.html"
    roots = (Path(__file__).resolve().parents[1] / "scripts", Path(__file__).resolve().parents[1] / "mcpb" / "src")
    program = f"""
from pathlib import Path
from cnki_search.results import parse_public_result_page

parsed = parse_public_result_page(Path({str(fixture)!r}).read_text(encoding='utf-8'), query='topic', limit=20)
assert [record.title for record in parsed.records] == ['First Missing Row Close', 'Second Complete Row']
assert parsed.incomplete_records == []
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


def test_nested_table_mutation_keeps_all_outer_rows(fixtures: Path) -> None:
    html = (fixtures / "public_results_stage3b.html").read_text(encoding="utf-8")
    without_nested_table = html.replace(
        '<table class="footnote"><tr><td>display only</td></tr></table>', ""
    )
    nested = results.parse_public_result_page(html, query="主题", limit=20)
    baseline = results.parse_public_result_page(without_nested_table, query="主题", limit=20)
    assert [record.title for record in nested.records] == [record.title for record in baseline.records]
    assert nested.total_rows == baseline.total_rows == 2


def test_unclosed_nested_table_mutation_stops_on_contract_change(fixtures: Path) -> None:
    html = (fixtures / "public_results_stage3b.html").read_text(encoding="utf-8")
    malformed = html.replace("</table>", "", 1)
    with pytest.raises(PageContractChanged, match="题录"):
        results.parse_public_result_page(malformed, query="主题", limit=20)


def test_result_table_without_any_row_is_loud_not_silent() -> None:
    """有结果表容器却解析出 0 行时必须报错，不得静默返回"无结果"。"""
    with pytest.raises(PageContractChanged, match="未解析出任何题录"):
        results.parse_public_result_page(
            "<table class='result-table-list'><tbody></tbody></table>", query="主题", limit=20
        )


def test_unclosed_cell_does_not_silently_drop_remaining_records() -> None:
    row = (
        "<tr><td class='name'><a>合法题录</a></td>"
        "<td class='source'><a>经济研究</a></td>"
        "<td class='date'>2024</td><td class='data'>期刊</td></tr>"
    )
    html = f"<table class='result-table-list'><tbody><tr><td class='name'><a>未闭合</a></tbody>{row}</table>"
    parsed = results.parse_public_result_page(html, query="主题", limit=20)
    assert [record.title for record in parsed.records] == ["合法题录"]


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
