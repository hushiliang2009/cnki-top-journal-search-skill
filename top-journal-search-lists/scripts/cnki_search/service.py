from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from catalog_lookup import DEFAULT_CATALOG

from .browser import BrowserUnavailableError
from .cache import SearchCache
from .models import SearchOutcome, SearchRequest, SearchStatus
from .ranking import annotate_and_sort_records
from .rate_limit import SerialSearchGate
from .results import parse_public_result_page
from .session import PublicCnkiSession, TransientBrowserError, classify_public_search_state
from .search import PageContractChanged


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_outcome(status: SearchStatus, query: str, warning: str = "") -> SearchOutcome:
    return SearchOutcome(status, query, [], [], 0, [warning] if warning else [], utc_now())


def _redact_paths(message: str) -> str:
    """去掉异常消息里的本机绝对路径，只保留文件名。

    异常消息会经 warnings 原样回传给 MCP 客户端，不得泄漏本机目录结构。
    """
    return re.sub(r"(?:[A-Za-z]:)?[\\/][^\s:：，,]*[\\/]([^\s\\/:：，,]+)", r"\1", message)


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
        # 目录缺失是部署配置错误，重试毫无意义，只会白打一次 CNKI。
        # 必须在限速门与浏览器启动之前拦下，且不得报成 network_error。
        if not self.catalog.is_file():
            return empty_outcome(
                SearchStatus.PAGE_CONTRACT_CHANGED,
                request.query,
                f"综合期刊目录不可用：{self.catalog.name}，请重新安装 Skill 或设置 CNKI_CATALOG_PATH",
            )
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
                return empty_outcome(
                    SearchStatus.PAGE_CONTRACT_CHANGED, request.query, _redact_paths(str(exc))
                )
            except BrowserUnavailableError as exc:
                # 本机没有可用浏览器属安装问题，重试无意义；转结构化状态并
                # 携带可操作提示，避免原始 traceback 穿透 MCP 工具边界。
                return empty_outcome(SearchStatus.NETWORK_ERROR, request.query, str(exc))
            except FileNotFoundError as exc:
                # FileNotFoundError ⊂ OSError：若不单列，配置错误会被下面的分支
                # 吞成 network_error，并白白重试一次。
                return empty_outcome(
                    SearchStatus.PAGE_CONTRACT_CHANGED, request.query, _redact_paths(str(exc))
                )
            except (TransientBrowserError, TimeoutError, OSError) as exc:
                if attempt == 1:
                    return empty_outcome(
                        SearchStatus.NETWORK_ERROR, request.query, _redact_paths(str(exc))
                    )
        raise AssertionError("unreachable")
