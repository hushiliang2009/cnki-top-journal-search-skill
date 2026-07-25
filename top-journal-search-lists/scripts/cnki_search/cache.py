from __future__ import annotations

import copy
import time
import unicodedata
from threading import RLock
from collections import OrderedDict

from .models import SearchOutcome


def normalize_cache_query(query: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", query).split()).casefold()


DEFAULT_MAX_ENTRIES = 1024


class SearchCache:
    def __init__(
        self, *, ttl_seconds: float = 86400, now=time.time, max_entries: int = DEFAULT_MAX_ENTRIES,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.now = now
        self.max_entries = max_entries
        # OrderedDict 充当 LRU：无上限的运行期缓存会随会话时长单调增长。
        self._items: OrderedDict[tuple[str, int], tuple[float, SearchOutcome]] = OrderedDict()
        self._lock = RLock()

    def get(self, query: str, limit: int) -> SearchOutcome | None:
        with self._lock:
            self._purge_expired()
            key = (normalize_cache_query(query), limit)
            item = self._items.get(key)
            if item is None:
                return None
            _expires_at, outcome = item
            self._items.move_to_end(key)
            return copy.deepcopy(outcome)

    def put(self, query: str, limit: int, outcome: SearchOutcome) -> None:
        with self._lock:
            key = (normalize_cache_query(query), limit)
            self._items[key] = (self.now() + self.ttl_seconds, copy.deepcopy(outcome))
            self._items.move_to_end(key)
            while len(self._items) > self.max_entries:
                self._items.popitem(last=False)

    def _purge_expired(self) -> None:
        current_time = self.now()
        for key, (expires_at, _outcome) in list(self._items.items()):
            if current_time >= expires_at:
                self._items.pop(key, None)
