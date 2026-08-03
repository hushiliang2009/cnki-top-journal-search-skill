from pathlib import Path

from cnki_search_env.models import PaperRecord
from cnki_search_env.ranking import annotate_and_sort_records


ROOT = Path(__file__).resolve().parents[1]
CATALOG_JSON = ROOT / "references" / "environment_journal_catalog_v4.0.json"


def record(journal: str, rank: int) -> PaperRecord:
    return PaperRecord(
        title="示例论文", authors=["张三"], journal_raw=journal, publication_date="2026",
        publication_year=2026, document_type="期刊", citations=None, downloads=None,
        is_online_first=False, result_rank=rank, source_database="CNKI", search_query="主题",
    )


def test_annotation_propagates_v4_record_identity_and_source_evidence() -> None:
    ranked = annotate_and_sort_records([record("城市规划", 1)], catalog=CATALOG_JSON)
    item = ranked[0]
    assert item.journal_id and item.journal_id.startswith("ENVJ-")
    assert item.catalog_version == "4.0"
    assert item.catalog_date == "2026-07-29"
    assert item.revision_date == "2026-07-31"
    assert set(item.index_memberships) == {"CSSCI", "PKU_CORE"}
    assert "CSSCI" in item.index_subject_categories
    assert item.source_memberships


def test_annotation_preserves_empty_v4_metadata_for_unmatched_records() -> None:
    item = annotate_and_sort_records([record("未知期刊", 1)], catalog=CATALOG_JSON)[0]
    assert item.journal_match_status == "unmatched"
    assert item.journal_id is None
    assert item.aliases == []
    assert item.index_subject_categories == {}
    assert item.source_memberships == []
    assert item.manual_review_required is True
