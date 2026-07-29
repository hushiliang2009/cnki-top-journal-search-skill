"""人工值守模式下的专业检索服务。

把四件既有能力串起来，自身不重复实现任何一件：

1. :mod:`professional` —— 按知网官方语法构造表达式并分批
2. :mod:`webvpn` —— 会话、节流、风控暂停与断点续跑
3. :func:`results.parse_public_result_page` —— 结果页解析（与公开模式同一套契约）
4. :func:`ranking.annotate_and_sort_records` —— 十级期刊目录标注与排序

检索范围**只限中文学术期刊论文**。这一约束靠三层保证，缺一不可：表达式层不使用
跨库字段；页面层由调用方把检索范围设为学术期刊、语种设为中文；解析层由
``parse_public_result_page`` 丢弃 ``document_type != "期刊"`` 的行。页面设置未必
随会话保持，表达式又表达不了文献类型，因此解析层的兜底不能省。
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from catalog_lookup import DEFAULT_CATALOG, journals_by_group

from .models import PaperRecord, SearchStatus
from .professional import (
    DEFAULT_MAX_EXPRESSION_CHARS,
    ExpressionBatch,
    build_batches,
    build_expression,
    build_topic_expression,
)
from .ranking import annotate_and_sort_records
from .results import parse_public_result_page
from .search import PageContractChanged
from .webvpn import BatchCheckpoint, Throttle, run_batches

#: 中文顶尖期刊（13 本）——本模式的核心收益，单条表达式即可覆盖。
CHINESE_TOP_GROUP = "chinese_top_journals"
#: CSSCI 来源期刊（661 本）。原表 674 行中的 13 本按 highest_priority_wins
#: 归入中文顶尖期刊，因此这里不含它们。
CSSCI_GROUP = "cssci"
SUPPORTED_GROUPS = (CHINESE_TOP_GROUP, CSSCI_GROUP)


@dataclass(frozen=True, slots=True)
class BatchOutcome:
    """单个批次的原始结果，尚未跨批次去重。"""

    index: int
    status: str
    records: tuple[PaperRecord, ...] = ()
    incomplete_records: tuple[PaperRecord, ...] = ()
    total_rows: int = 0
    excluded_non_journal_rows: int = 0
    result_url: str | None = None
    detail: str | None = None


#: 页面驱动：接收完整执行计划，返回 ``(status, html, url)``。
#: 真实实现驱动浏览器；测试注入假实现即可完全离线。
ExpressionExecutor = Callable[[ExpressionBatch], Awaitable[tuple[str, str, str]]]


class CnkiProfessionalSearchService:
    def __init__(self, executor: ExpressionExecutor, *,
                 catalog: Path = DEFAULT_CATALOG,
                 max_expression_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
                 throttle: Throttle | None = None,
                 checkpoint: BatchCheckpoint | None = None,
                 on_challenge: Callable[[ExpressionBatch], Awaitable[bool]] | None = None) -> None:
        self.executor = executor
        self.catalog = catalog
        self.max_expression_chars = max_expression_chars
        self.throttle = throttle
        self.checkpoint = checkpoint
        self.on_challenge = on_challenge

    async def search_group(self, topic: str, group: str, *, limit: int = 20,
                           year_from: int | None = None,
                           year_to: int | None = None) -> dict[str, Any]:
        """按目录层级检索：期刊清单直接取自综合期刊目录，不手工维护副本。"""
        if group not in SUPPORTED_GROUPS:
            raise ValueError(
                f"CNKI 专业检索只覆盖中文层级 {SUPPORTED_GROUPS}，收到 {group!r}"
            )
        batches = build_group_plans(
            topic,
            group,
            catalog=self.catalog,
            max_chars=self.max_expression_chars,
            year_from=year_from,
            year_to=year_to,
        )
        summary = await self._run(batches, limit)
        summary["group"] = group
        if group == CHINESE_TOP_GROUP:
            summary["journal_count"] = 13
        else:
            summary["journal_count"] = None
            summary["source_category"] = "CSSCI"
        return summary

    async def search_expression(self, expression: str, *, limit: int = 20) -> dict[str, Any]:
        """直接执行一条使用者自备的专业检索表达式，不做分批。"""
        batch = ExpressionBatch(index=1, total=1, journals=(), expression=expression)
        return await self._run([batch], limit)

    async def _run(self, batches: list[ExpressionBatch], limit: int) -> dict[str, Any]:
        async def execute(batch: ExpressionBatch) -> dict[str, Any]:
            status, html, url = await self.executor(batch)
            if status != SearchStatus.SUCCESS.value:
                return {"index": batch.index, "status": status, "result_url": url}
            try:
                parsed = parse_public_result_page(
                    html, query=batch.expression, limit=limit
                )
            except PageContractChanged as exc:
                return {
                    "index": batch.index,
                    "status": SearchStatus.PAGE_CONTRACT_CHANGED.value,
                    "result_url": url,
                    "detail": str(exc),
                }
            return {
                "index": batch.index,
                "status": SearchStatus.SUCCESS.value,
                "result_url": url,
                "total_rows": parsed.total_rows,
                "excluded_non_journal_rows": parsed.excluded_non_journal_rows,
                "records": parsed.records,
                "incomplete_records": parsed.incomplete_records,
            }

        schedule = await run_batches(batches, execute, on_challenge=self.on_challenge,
                                     checkpoint=self.checkpoint, throttle=self.throttle)
        return self._merge(schedule, batches)

    def _merge(self, schedule: dict[str, Any], batches: list[ExpressionBatch]) -> dict[str, Any]:
        records: list[PaperRecord] = []
        incomplete: list[PaperRecord] = []
        total_rows = excluded = 0
        seen: set[tuple[str, str, int | None]] = set()
        for item in schedule["results"]:
            total_rows += item.get("total_rows", 0)
            excluded += item.get("excluded_non_journal_rows", 0)
            for record in item.get("records", ()):
                key = (record.title, record.journal_raw, record.publication_year)
                if key in seen:          # 同一篇论文可能落在相邻批次的边界上
                    continue
                seen.add(key)
                records.append(record)
            incomplete.extend(item.get("incomplete_records", ()))

        annotated = annotate_and_sort_records(records, catalog=self.catalog)
        stopped_result = schedule.get("stopped_result")
        contract_changed = (
            stopped_result
            if stopped_result
            and stopped_result.get("status")
            == SearchStatus.PAGE_CONTRACT_CHANGED.value
            else None
        )
        complete = schedule["complete"] and contract_changed is None
        if contract_changed is not None:
            status = SearchStatus.PAGE_CONTRACT_CHANGED
        elif not annotated:
            status = (
                SearchStatus.NO_RESULTS if complete else SearchStatus.PARTIAL
            )
        else:
            status = SearchStatus.SUCCESS if complete and not incomplete else SearchStatus.PARTIAL
        result = {
            "ok": contract_changed is None,
            "mode": "webvpn",
            "status": status.value,
            "complete": complete,
            "batches_completed": schedule["batches_completed"],
            "batches_total": schedule["batches_total"],
            "stopped_at_batch": schedule["stopped_at_batch"],
            # 显式暴露：本模式必须有人值守，调用方不得据此安排无人值守任务
            "human_intervention_required": schedule["human_intervention_required"],
            "expressions": [batch.expression for batch in batches],
            "total_rows": total_rows,
            "excluded_non_journal_rows": excluded,
            "records": [record.to_dict() for record in annotated],
            "incomplete_records": [record.to_dict() for record in incomplete],
        }
        if contract_changed is not None:
            result["detail"] = contract_changed.get(
                "detail", "知网页面结构已变化"
            )
        return result


def build_group_plans(
    topic: str,
    group: str,
    *,
    catalog: Path = DEFAULT_CATALOG,
    max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[ExpressionBatch]:
    if group == CHINESE_TOP_GROUP:
        return build_batches(
            topic,
            journals_by_group(group, catalog),
            year_from=year_from,
            year_to=year_to,
            max_chars=max_chars,
        )
    if group == CSSCI_GROUP:
        return [
            ExpressionBatch(
                index=1,
                total=1,
                journals=(),
                expression=build_topic_expression(
                    topic, year_from=year_from, year_to=year_to
                ),
                source_category="CSSCI",
            )
        ]
    raise ValueError(
        f"CNKI 专业检索只覆盖中文层级 {SUPPORTED_GROUPS}，收到 {group!r}"
    )


def preview_plans(
    topic: str,
    group: str,
    *,
    catalog: Path = DEFAULT_CATALOG,
    max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[ExpressionBatch]:
    return build_group_plans(
        topic,
        group,
        catalog=catalog,
        max_chars=max_chars,
        year_from=year_from,
        year_to=year_to,
    )


def preview_expressions(topic: str, group: str, *, catalog: Path = DEFAULT_CATALOG,
                        max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
                        year_from: int | None = None,
                        year_to: int | None = None) -> list[str]:
    """不触网地预览将要提交的表达式，便于人工复核覆盖范围。"""
    return [
        batch.expression
        for batch in preview_plans(
            topic,
            group,
            catalog=catalog,
            max_chars=max_chars,
            year_from=year_from,
            year_to=year_to,
        )
    ]


__all__ = [
    "CHINESE_TOP_GROUP",
    "CSSCI_GROUP",
    "SUPPORTED_GROUPS",
    "BatchOutcome",
    "CnkiProfessionalSearchService",
    "ExpressionBatch",
    "ExpressionExecutor",
    "build_group_plans",
    "build_expression",
    "build_topic_expression",
    "preview_plans",
    "preview_expressions",
]
