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


def test_cache_rejects_session_and_address_fields() -> None:
    """规格第九节要求缓存不得保存 URL 或会话字段，该守卫必须有测试守住。"""
    import pytest

    from cnki_search.models import PaperRecord, SearchOutcome

    cache = SearchCache()
    record = PaperRecord(
        title="题录", authors=["张三"], journal_raw="经济研究", publication_date="2024",
        publication_year=2024, document_type="期刊", citations=None, downloads=None,
        is_online_first=False, result_rank=1, source_database="CNKI", search_query="主题",
    )
    outcome = SearchOutcome(SearchStatus.SUCCESS, "主题", [record], [], 0, [], "now")
    # 模拟题录意外带上地址字段
    object.__setattr__(outcome, "warnings", ["ok"])
    payload_record = record.to_dict()
    payload_record["detail_url"] = "https://kns.cnki.net/kcms2/article?v=1"

    class LeakyOutcome(SearchOutcome):
        def to_dict(self):  # type: ignore[override]
            data = super().to_dict()
            data["records"] = [payload_record]
            return data

    leaky = LeakyOutcome(SearchStatus.SUCCESS, "主题", [record], [], 0, [], "now")
    with pytest.raises(ValueError, match="会话或地址字段"):
        cache.put("主题", 20, leaky)


def test_cache_evicts_least_recently_used_beyond_capacity() -> None:
    cache = SearchCache(max_entries=2)
    for name in ("甲", "乙"):
        cache.put(name, 20, empty_outcome(SearchStatus.SUCCESS, name))
    cache.get("甲", 20)                       # 甲 变为最近使用
    cache.put("丙", 20, empty_outcome(SearchStatus.SUCCESS, "丙"))
    assert cache.get("乙", 20) is None          # 最久未使用的被淘汰
    assert cache.get("甲", 20) is not None
    assert cache.get("丙", 20) is not None


def test_request_and_cache_share_one_whitespace_normalization() -> None:
    """缓存键与检索词归一化口径必须一致，否则返回的 query 会失真。"""
    from cnki_search.cache import normalize_cache_query
    from cnki_search.models import SearchRequest

    for raw in ("数字化  转型", " 数字化　转型 ", "数字化\t转型"):
        assert SearchRequest(raw).query == "数字化 转型"
        assert normalize_cache_query(raw) == normalize_cache_query("数字化 转型")
