from cnki_search_env.cache import SearchCache, normalize_cache_query
from cnki_search_env.models import SearchOutcome, SearchStatus
from cnki_search_env.service import empty_outcome


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
    cache.put("topic phrase", 20, empty_outcome(SearchStatus.SUCCESS, "topic phrase"))
    assert cache.get("TOPIC\tphrase", 20).status is SearchStatus.SUCCESS
    clock.advance(86401)
    assert cache.get("topic phrase", 20) is None


def test_cache_does_not_inspect_unreachable_serialized_field_names() -> None:
    class LeakyOutcome(SearchOutcome):
        def to_dict(self):  # type: ignore[override]
            data = super().to_dict()
            data["detail_url"] = "https://example.invalid/record"
            return data

    outcome = LeakyOutcome(SearchStatus.SUCCESS, "topic", [], [], 0, [], "now")
    cache = SearchCache()
    cache.put("topic", 20, outcome)
    assert cache.get("topic", 20) is not None


def test_cache_evicts_least_recently_used_beyond_capacity() -> None:
    cache = SearchCache(max_entries=2)
    for query in ("first", "second"):
        cache.put(query, 20, empty_outcome(SearchStatus.SUCCESS, query))
    cache.get("first", 20)
    cache.put("third", 20, empty_outcome(SearchStatus.SUCCESS, "third"))
    assert cache.get("second", 20) is None
    assert cache.get("first", 20) is not None
    assert cache.get("third", 20) is not None


def test_default_capacity_evicts_only_the_least_recent_entry() -> None:
    cache = SearchCache()
    for index in range(1025):
        query = f"topic-{index}"
        cache.put(query, 20, empty_outcome(SearchStatus.SUCCESS, query))
    assert cache.get("topic-0", 20) is None
    assert cache.get("topic-1", 20) is not None
    assert cache.get("topic-1024", 20) is not None


def test_cache_read_removes_all_expired_entries() -> None:
    clock = FakeClock()
    cache = SearchCache(now=clock)
    for query in ("first", "second"):
        cache.put(query, 20, empty_outcome(SearchStatus.SUCCESS, query))
    clock.advance(86400)
    assert cache.get("missing", 20) is None
    assert cache._items == {}


def test_request_and_cache_share_normalization_with_casefold_only_in_cache_key() -> None:
    from cnki_search_env.models import SearchRequest

    request = SearchRequest("  ＡＢＣ　Topic  ")
    assert request.query == "ABC Topic"
    assert normalize_cache_query(request.query) == normalize_cache_query("abc\ttopic")
