import json
from pathlib import Path

import pytest

from cnki_search.cache import MetadataCache


TEST_CACHE = Path(__file__).with_name("_metadata_cache_test.json")


def _remove_test_cache() -> None:
    TEST_CACHE.unlink(missing_ok=True)


def test_cache_rejects_sensitive_keys() -> None:
    _remove_test_cache()
    try:
        cache = MetadataCache(TEST_CACHE)
        with pytest.raises(ValueError, match="敏感"):
            cache.put("q", {"nested": {"cookie": "x"}})
    finally:
        _remove_test_cache()


def test_cache_writes_only_metadata() -> None:
    _remove_test_cache()
    try:
        cache = MetadataCache(TEST_CACHE)
        cache.put("q", {"title": "数字化转型", "year": 2025})
        assert json.loads(TEST_CACHE.read_text(encoding="utf-8"))["q"]["year"] == 2025
    finally:
        _remove_test_cache()
