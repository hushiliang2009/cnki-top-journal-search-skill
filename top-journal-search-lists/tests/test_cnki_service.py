from pathlib import Path

import pytest

from cnki_search.models import SearchStatus
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


class CountingGate:
    def __init__(self) -> None:
        self.calls = 0

    def wait(self) -> float:
        self.calls += 1
        return 0.0


class SequenceFactory:
    def __init__(self, snapshots: list[SearchSnapshot]) -> None:
        self.snapshots = snapshots
        self.calls = 0

    def __call__(self) -> "SequenceFactory":
        return self

    def __enter__(self) -> "SequenceFactory":
        self.calls += 1
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def search(self, _query: str) -> SearchSnapshot:
        return self.snapshots[self.calls - 1]


def _snapshot(*, url: str = "https://kns.cnki.net/kns8s/defaultresult/index", text: str = "题名 来源", status: int | None = 200) -> SearchSnapshot:
    return SearchSnapshot("<table class='result-table-list'></table>", url, "中国知网", text, status)


def test_network_error_retries_once_only() -> None:
    factory = SequenceFactory([_snapshot(status=500), _snapshot(status=500)])
    gate = CountingGate()
    outcome = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题")
    assert outcome.status is SearchStatus.NETWORK_ERROR
    assert (factory.calls, gate.calls) == (2, 2)


@pytest.mark.parametrize(
    "snapshot, expected",
    [
        (_snapshot(text="429 Too Many Requests"), SearchStatus.RATE_LIMITED),
        (_snapshot(url="https://kns.cnki.net/captcha", text="请完成拼图验证"), SearchStatus.CHALLENGE_DETECTED),
        (_snapshot(url="https://login.cnki.net/", text="用户登录"), SearchStatus.LOGIN_REQUIRED),
        (_snapshot(text="403 Forbidden"), SearchStatus.FORBIDDEN),
        (_snapshot(url="https://example.invalid/", text="结构变化"), SearchStatus.PAGE_CONTRACT_CHANGED),
    ],
)
def test_restricted_or_changed_state_never_retries(snapshot: SearchSnapshot, expected: SearchStatus) -> None:
    factory = SequenceFactory([snapshot])
    gate = CountingGate()
    outcome = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate).search("主题")
    assert outcome.status is expected
    assert (factory.calls, gate.calls) == (1, 1)


def test_cache_hit_skips_session_and_gate() -> None:
    factory = SequenceFactory([_snapshot(text="未检索到相关文献")])
    gate = CountingGate()
    service = CnkiPublicSearchService(session_factory=factory, catalog=CATALOG, gate=gate)
    assert service.search("主题").status is SearchStatus.NO_RESULTS
    assert service.search("主题").status is SearchStatus.NO_RESULTS
    assert (factory.calls, gate.calls) == (1, 1)
