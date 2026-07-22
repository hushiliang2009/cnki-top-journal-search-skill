from __future__ import annotations

import copy
import time
import unicodedata
from collections.abc import Iterable
from typing import Any

from .models import SearchOutcome


def normalize_cache_query(query: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", query).split()).casefold()


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


class SearchCache:
    def __init__(self, *, ttl_seconds: float = 86400, now=time.time) -> None:
        self.ttl_seconds = ttl_seconds
        self.now = now
        self._items: dict[tuple[str, int], tuple[float, SearchOutcome]] = {}

    def get(self, query: str, limit: int) -> SearchOutcome | None:
        key = (normalize_cache_query(query), limit)
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, outcome = item
        if self.now() >= expires_at:
            self._items.pop(key, None)
            return None
        return copy.deepcopy(outcome)

    def put(self, query: str, limit: int, outcome: SearchOutcome) -> None:
        payload = outcome.to_dict()
        forbidden = {"cookie", "token", "url", "password", "storage_state"}
        if any(any(part in key.casefold() for part in forbidden) for key in _walk_keys(payload)):
            raise ValueError("缓存包含会话或地址字段")
        key = (normalize_cache_query(query), limit)
        self._items[key] = (self.now() + self.ttl_seconds, copy.deepcopy(outcome))
