from cnki_search.merge import merge_literature_results
from cnki_search.models import PaperRecord


def test_merge_keeps_primary_and_cnki_provenance() -> None:
    primary = [{"title": "数字化转型与企业创新", "authors": ["张三"], "year": 2026}]
    cnki = [
        PaperRecord(
            title="数字化转型与企业创新", authors=["张三"], journal_raw="经济研究",
            publication_date="2026", publication_year=2026, document_type="期刊",
            citations=None, downloads=None, is_online_first=False, result_rank=1,
            source_database="CNKI", search_query="主题",
        )
    ]
    merged = merge_literature_results(primary, cnki)
    assert len(merged) == 1
    assert merged[0]["sources"] == ["ai4scholar", "CNKI"]
    assert set(merged[0]["source_records"]) == {"ai4scholar", "CNKI"}
