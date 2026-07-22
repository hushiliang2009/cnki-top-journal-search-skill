from pathlib import Path

from cnki_search.models import PaperRecord
from cnki_search.ranking import annotate_and_sort_records


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "Academic_Journal_Master_Directory_20260715.md"


def record(journal: str, rank: int) -> PaperRecord:
    return PaperRecord(
        title="示例论文", authors=["张三"], journal_raw=journal, publication_date="2026",
        publication_year=2026, document_type="期刊", citations=None, downloads=None,
        is_online_first=False, result_rank=rank, source_database="CNKI", search_query="主题",
    )


def test_annotation_uses_catalog_and_preserves_unmatched() -> None:
    records = [record("未知期刊", 1), record("经济研究", 2)]
    ranked = annotate_and_sort_records(records, catalog=CATALOG)
    assert [item.journal_raw for item in ranked] == ["经济研究", "未知期刊"]
    assert ranked[0].priority_level == 6
    assert "经济学" in ranked[0].subject_categories
    assert ranked[1].journal_match_status == "unmatched"
    assert ranked[1].manual_review_required is True
