from pathlib import Path

from cnki_search.service import CnkiPublicSearchService
from cnki_search.session import SearchSnapshot


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "Academic_Journal_Master_Directory_20260715.md"
FIXTURES = Path(__file__).with_name("fixtures")


class FakeSession:
    def __init__(self, html: str) -> None:
        self.html = html

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def search(self, query: str) -> SearchSnapshot:
        return SearchSnapshot(
            self.html, "https://kns.cnki.net/kns8s/defaultresult/index",
            "检索-中国知网", "题名 作者 来源 日期 数据库", 200,
        )


def test_service_returns_partial_when_incomplete_rows_exist() -> None:
    html = (FIXTURES / "public_incomplete_results.html").read_text(encoding="utf-8")
    service = CnkiPublicSearchService(session_factory=lambda: FakeSession(html), catalog=CATALOG)
    outcome = service.search("数字化转型", limit=20)
    assert outcome.status.value == "partial"
    assert all(item.title and item.journal_raw and item.publication_year for item in outcome.records)
    assert outcome.incomplete_records
