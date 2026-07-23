from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from catalog_lookup import DEFAULT_CATALOG, validate_catalog

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


# 受限状态本身不说明"该主题无文献"。必须给出可操作的替代路径，否则调用方
# 容易把一次未能执行的检索写成"未检索到相关文献"。
_FALLBACK_HINTS = {
    SearchStatus.CHALLENGE_DETECTED: (
        "知网触发了站点安全验证，这是站点侧正常防护，不是安装故障，重试无效。"
        "请改用 ai4scholar 检索；如需中文近期文献，可自行在知网网页端检索后，"
        "用 catalog_lookup.py lookup 对期刊判级。本次未取得任何 CNKI 题录，"
        "不能据此判断该主题无中文文献。"
    ),
    SearchStatus.LOGIN_REQUIRED: (
        "知网要求登录，本工具不登录也不使用你的浏览器配置文件。"
        "请改用 ai4scholar；本次未取得任何 CNKI 题录。"
    ),
    SearchStatus.FORBIDDEN: (
        "知网拒绝了本次公开访问。请改用 ai4scholar；本次未取得任何 CNKI 题录。"
    ),
    SearchStatus.RATE_LIMITED: (
        "知网提示访问过于频繁。请稍后再试或改用 ai4scholar；本次未取得任何 CNKI 题录。"
    ),
}


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
        try:
            request = SearchRequest(query, limit)
        except ValueError as exc:
            # 参数非法是可预期的调用错误，应走结构化状态而不是 MCP 的 isError，
            # 否则调用方拿不到 status 也拿不到 warnings。
            return empty_outcome(SearchStatus.PAGE_CONTRACT_CHANGED, str(query), str(exc))
        # 目录问题是部署配置错误，必须在缓存、限速与浏览器启动之前拦下。
        # 此处同时校验目录结构，避免格式损坏时访问 CNKI 或触发无意义重试。
        try:
            validate_catalog(self.catalog)
        except (FileNotFoundError, OSError, ValueError):
            return empty_outcome(
                SearchStatus.CONFIGURATION_ERROR,
                request.query,
                f"期刊目录不可用：{self.catalog.name}，请重新安装或指定有效目录。",
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
                    return empty_outcome(status, request.query, _FALLBACK_HINTS.get(status, ""))
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
            except (TransientBrowserError, TimeoutError, OSError) as exc:
                if attempt == 1:
                    return empty_outcome(
                        SearchStatus.NETWORK_ERROR, request.query, _redact_paths(str(exc))
                    )
        raise AssertionError("unreachable")
