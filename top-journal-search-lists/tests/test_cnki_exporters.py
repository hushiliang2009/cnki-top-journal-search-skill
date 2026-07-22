import json
from pathlib import Path

from cnki_search.exporters import (
    attach_journal_levels,
    deduplicate_records,
    export_records,
)
from cnki_search.models import PaperRecord


def _records() -> list[PaperRecord]:
    return [
        PaperRecord(
            title="数字化转型与企业创新",
            authors=["张三", "李四"],
            first_author="张三",
            journal="经济研究",
            year=2025,
            volume="60",
            issue="1",
            pages="1-20",
            keywords=["数字化转型", "企业创新"],
            doi="10.1234/EXAMPLE.1",
        ),
        PaperRecord(
            title=" 数字化转型与企业创新 ",
            authors=["张三"],
            first_author="张三",
            journal="经济研究",
            year=2025,
            doi="https://doi.org/10.1234/example.1",
        ),
        PaperRecord(
            title="Climate Risk and Asset Prices",
            authors=["Alice Smith"],
            first_author="Alice Smith",
            journal="American Economic Review",
            year=2024,
        ),
    ]


def test_deduplicate_prefers_doi_then_title_author_year() -> None:
    unique = deduplicate_records(_records())
    assert len(unique) == 2
    assert unique[0].title == "数字化转型与企业创新"


def test_attach_journal_levels_uses_master_catalog() -> None:
    records = attach_journal_levels(_records()[2:])
    assert records[0].journal_level == "1:economics_top5"


def test_export_json_csv_bibtex_ris_and_gbt7714(skill_root: Path) -> None:
    records = deduplicate_records(_records())
    output_dir = skill_root / "tests" / "_export_test"
    output_dir.mkdir(exist_ok=True)
    try:
        paths = export_records(records, output_dir, stem="cnki")
        assert set(paths) == {"json", "csv", "bibtex", "ris", "gbt7714"}
        payload = json.loads(paths["json"].read_text(encoding="utf-8"))
        assert payload[0]["doi"] == "10.1234/EXAMPLE.1"
        assert paths["csv"].read_bytes().startswith(b"\xef\xbb\xbf")
        assert "@article{" in paths["bibtex"].read_text(encoding="utf-8")
        assert "TY  - JOUR" in paths["ris"].read_text(encoding="utf-8")
        assert "[J]" in paths["gbt7714"].read_text(encoding="utf-8")
    finally:
        for path in output_dir.glob("cnki.*"):
            path.unlink()
        output_dir.rmdir()
