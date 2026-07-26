from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path

from .browser import BrowserUnavailableError, prepare_browser_runtime
from .cache import SearchCache
from .catalog_adapter import DEFAULT_CATALOG, validate_catalog
from .models import SearchOutcome, SearchRequest, SearchStatus
from .ranking import annotate_and_sort_records
from .rate_limit import SerialSearchGate
from .results import parse_public_result_page
from .session import PublicCnkiSession, TransientBrowserError, classify_public_search_state
from .search import PageContractChanged

SEARCH_TIMEOUT_SECONDS = 30.0

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def empty_outcome(status: SearchStatus, query: str, warning: str = "") -> SearchOutcome:
    return SearchOutcome(status, query, [], [], 0, [warning] if warning else [], utc_now())

_CHALLENGE_WARNING = "知网安全验证已阻止本次检索；已停止请求，请不要刷新、重试或切换代理。可继续使用 ai4scholar，或在浏览器手动检索下载。"
_SHORT_WARNINGS = {
    SearchStatus.LOGIN_REQUIRED: "需要登录", SearchStatus.FORBIDDEN: "访问被拒绝",
    SearchStatus.RATE_LIMITED: "访问频繁", SearchStatus.PAGE_CONTRACT_CHANGED: "页面结构变化",
    SearchStatus.CONFIGURATION_ERROR: "配置错误", SearchStatus.NETWORK_ERROR: "网络错误",
}

class CnkiPublicSearchService:
    def __init__(self, *, session_factory=PublicCnkiSession, catalog: Path = DEFAULT_CATALOG,
                 cache: SearchCache | None = None, gate: SerialSearchGate | None = None,
                 search_timeout_seconds: float = SEARCH_TIMEOUT_SECONDS,
                 browser_preparer: Callable[[], Awaitable[None]] | None = None) -> None:
        self.session_factory = session_factory
        self.catalog = catalog
        self.cache = cache or SearchCache()
        self.gate = gate or SerialSearchGate()
        self.search_timeout_seconds = search_timeout_seconds
        self._search_lock = asyncio.Lock()
        self._browser_preparer = (
            prepare_browser_runtime
            if browser_preparer is None and session_factory is PublicCnkiSession
            else browser_preparer
        )
        self._browser_ready = self._browser_preparer is None
        self._browser_lock = asyncio.Lock()

    async def search(self, query: str, limit: int = 20) -> SearchOutcome:
        request = SearchRequest(query, limit)
        try:
            await self._prepare_browser()
        except BrowserUnavailableError:
            return empty_outcome(
                SearchStatus.CONFIGURATION_ERROR, request.query, "浏览器不可用",
            )
        try:
            return await asyncio.wait_for(self._search_from_entry(request), timeout=self.search_timeout_seconds)
        except asyncio.TimeoutError:
            return empty_outcome(SearchStatus.NETWORK_ERROR, request.query, _SHORT_WARNINGS[SearchStatus.NETWORK_ERROR])

    async def _prepare_browser(self) -> None:
        if self._browser_ready:
            return
        async with self._browser_lock:
            if self._browser_ready:
                return
            assert self._browser_preparer is not None
            await self._browser_preparer()
            self._browser_ready = True

    async def _search_from_entry(self, request: SearchRequest) -> SearchOutcome:
        try:
            await asyncio.to_thread(validate_catalog, self.catalog)
        except (FileNotFoundError, OSError, ValueError):
            return empty_outcome(SearchStatus.CONFIGURATION_ERROR, request.query, _SHORT_WARNINGS[SearchStatus.CONFIGURATION_ERROR])
        cached = await asyncio.to_thread(self.cache.get, request.query, request.limit)
        if cached is not None:
            cached.query = request.query
            return cached
        return await self._search_serialized(request)

    async def _search_serialized(self, request: SearchRequest) -> SearchOutcome:
        async with self._search_lock:
            for attempt in range(2):
                await self.gate.wait()
                try:
                    async with self.session_factory() as session:
                        snapshot = await session.search(request.query)
                    status = classify_public_search_state(**snapshot.state_arguments())
                    if status is SearchStatus.NETWORK_ERROR and attempt == 0:
                        continue
                    if status is SearchStatus.NO_RESULTS:
                        outcome = empty_outcome(status, request.query)
                    elif status is SearchStatus.CHALLENGE_DETECTED:
                        return empty_outcome(status, request.query, _CHALLENGE_WARNING)
                    elif status is not SearchStatus.SUCCESS:
                        return empty_outcome(status, request.query, _SHORT_WARNINGS.get(status, ""))
                    else:
                        parsed = parse_public_result_page(snapshot.html, query=request.query, limit=request.limit)
                        records = annotate_and_sort_records(parsed.records, catalog=self.catalog)
                        result_status = SearchStatus.PARTIAL if parsed.incomplete_records else (SearchStatus.SUCCESS if records else SearchStatus.NO_RESULTS)
                        outcome = SearchOutcome(result_status, request.query, records, parsed.incomplete_records,
                                                parsed.excluded_non_journal_rows, [], utc_now())
                    await asyncio.to_thread(self.cache.put, request.query, request.limit, outcome)
                    return outcome
                except PageContractChanged:
                    return empty_outcome(SearchStatus.PAGE_CONTRACT_CHANGED, request.query, _SHORT_WARNINGS[SearchStatus.PAGE_CONTRACT_CHANGED])
                except BrowserUnavailableError:
                    return empty_outcome(SearchStatus.CONFIGURATION_ERROR, request.query, "浏览器不可用")
                except (TransientBrowserError, TimeoutError, OSError):
                    if attempt == 1:
                        return empty_outcome(SearchStatus.NETWORK_ERROR, request.query, _SHORT_WARNINGS[SearchStatus.NETWORK_ERROR])
        raise AssertionError("unreachable")
