from cnki_search.cache import SearchCache
from cnki_search.models import SearchStatus
from cnki_search.service import empty_outcome


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def test_cache_expires_after_24_hours() -> None:
    clock = FakeClock()
    cache = SearchCache(ttl_seconds=86400, now=clock)
    outcome = empty_outcome(SearchStatus.SUCCESS, "数字化 转型")
    cache.put("数字化 转型", 20, outcome)
    assert cache.get("数字化　转型", 20).status is SearchStatus.SUCCESS
    clock.advance(86401)
    assert cache.get("数字化 转型", 20) is None
