from pathlib import Path

from cnki_search.results import parse_result_page


def test_result_page_parses_required_metadata() -> None:
    html = (Path(__file__).with_name("fixtures") / "results.html").read_text(encoding="utf-8")
    records = parse_result_page(html, base_url="https://kns.cnki.net")
    assert len(records) == 2
    assert records[0].title == "数字化转型与企业创新"
    assert records[0].authors == ["张三", "李四"]
    assert records[0].first_author == "张三"
    assert records[0].journal == "经济研究"
    assert records[0].year == 2025
    assert records[0].doi == "10.1234/example.1"
    assert records[0].detail_url == "https://kns.cnki.net/detail/1"
    assert records[0].keywords == ["数字化转型", "企业创新"]


def test_real_cnki_result_table_parses_rows_and_nested_title_text() -> None:
    html = (Path(__file__).with_name("fixtures") / "results_table.html").read_text(
        encoding="utf-8"
    )
    records = parse_result_page(html, base_url="https://kns.cnki.net")
    assert len(records) == 2
    assert records[0].title == "数字化转型何以赋能探索式创新"
    assert records[0].authors == ["方鑫", "陆亮亮", "唐秋雨", "谢佩洪"]
    assert records[0].journal == "技术经济与管理研究"
    assert records[0].year == 2026
    assert records[0].detail_url == "https://kns.cnki.net/kcms2/article/abstract?id=1"
