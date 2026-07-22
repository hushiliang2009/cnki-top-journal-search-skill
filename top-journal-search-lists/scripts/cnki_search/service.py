from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from catalog_lookup import DEFAULT_CATALOG

from .cache import SearchCache
from .models import SearchOutcome, SearchRequest, SearchStatus
from .ranking import annotate_and_sort_records
from .rate_limit import SerialSearchGate
from .results import parse_public_result_page
from .session import PublicCnkiSession, classify_public_search_state
from .search import PageContractChanged


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_outcome(status: SearchStatus, query: str, warning: str = "") -> SearchOutcome:
    return SearchOutcome(status, query, [], [], 0, [warning] if warning else [], utc_now())


class CnkiPublicSearchService:
    def __init__(
        self, *, session_factory=PublicCnkiSession, catalog: Path = DEFAULT_CATALOG,
        cache: SearchCache | None = None, gate: SerialSearchGate | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.catalog = catalog
        self.cache = cache or SearchCache()
        self.gate = gate or SerialSearchGate()

    def search(self, query: str, limit: int = 20) -> SearchOutcome:
        request = SearchRequest(query, limit)
        cached = self.cache.get(request.query, request.limit)
        if cached is not None:
            return cached
        for attempt in range(2):
            self.gate.wait()
            try:
                with self.session_factory() as session:
                    snapshot = session.search(request.query)
                status = classify_public_search_state(**snapshot.state_arguments())
                if status is SearchStatus.NO_RESULTS:
                    outcome = empty_outcome(status, request.query)
                elif status is SearchStatus.NETWORK_ERROR and attempt == 0:
                    continue
                elif status is not SearchStatus.SUCCESS:
                    return empty_outcome(status, request.query)
                else:
                    parsed = parse_public_result_page(snapshot.html, query=request.query, limit=request.limit)
                    records = annotate_and_sort_records(parsed.records, catalog=self.catalog)
                    result_status = SearchStatus.PARTIAL if parsed.incomplete_records else (
                        SearchStatus.SUCCESS if records else SearchStatus.NO_RESULTS
                    )
                    outcome = SearchOutcome(
                        result_status, request.query, records, parsed.incomplete_records,
                        parsed.excluded_non_journal_rows, [], utc_now(),
                    )
                self.cache.put(request.query, request.limit, outcome)
                return outcome
            except PageContractChanged as exc:
                return empty_outcome(SearchStatus.PAGE_CONTRACT_CHANGED, request.query, str(exc))
            except (TimeoutError, OSError) as exc:
                if attempt == 1:
                    return empty_outcome(SearchStatus.NETWORK_ERROR, request.query, str(exc))
        raise AssertionError("unreachable")
