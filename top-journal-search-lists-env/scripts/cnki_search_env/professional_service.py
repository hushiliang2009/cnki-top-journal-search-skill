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

import unicodedata
from collections.abc import Awaitable, Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .catalog_adapter import DEFAULT_CATALOG, journals_by_group

from .models import PaperRecord, SearchStatus, is_verifiable_publication_year
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

#: 中文环境顶尖期刊（6 本）——本模式的核心收益，单条表达式即可覆盖。
CHINESE_ENVIRONMENT_TOP_GROUP = "chinese_environment_top"
#: 环境 CSSCI 来源期刊（241 本）。那 6 本中文环境顶刊按 highest_priority_wins
#: 归入 chinese_environment_top，因此这里不含它们。
ENVIRONMENT_CSSCI_GROUP = "environment_cssci"
SUPPORTED_GROUPS = (CHINESE_ENVIRONMENT_TOP_GROUP, ENVIRONMENT_CSSCI_GROUP)
#: 结果页左侧「来源类别」分面的取值。环境 CSSCI 只是 CSSCI 的子集，分面单独
#: 用收不窄到环境学科，因此分面与刊名枚举同时使用，两者都不能省。
CSSCI_SOURCE_CATEGORY = "CSSCI"


@dataclass(frozen=True, slots=True)
class BatchOutcome:
    """单个批次的原始结果，尚未跨批次去重。"""

    index: int
    status: str
    records: tuple[PaperRecord, ...] = ()
    incomplete_records: tuple[PaperRecord, ...] = ()
    total_rows: int = 0
    excluded_non_journal_rows: int = 0
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
        # 两组都是逐本枚举，刊数直接来自环境目录，不写死在代码里。
        summary["journal_count"] = len(journals_by_group(group, self.catalog))
        if group == ENVIRONMENT_CSSCI_GROUP:
            summary["source_category"] = CSSCI_SOURCE_CATEGORY
        return summary

    async def search_expression(self, expression: str, *, limit: int = 20) -> dict[str, Any]:
        """直接执行一条使用者自备的专业检索表达式，不做分批。"""
        batch = ExpressionBatch(index=1, total=1, journals=(), expression=expression)
        return await self._run([batch], limit)

    async def _run(self, batches: list[ExpressionBatch], limit: int) -> dict[str, Any]:
        async def execute(batch: ExpressionBatch) -> dict[str, Any]:
            status, html, _url = await self.executor(batch)
            if status != SearchStatus.SUCCESS.value:
                return {"index": batch.index, "status": status}
            try:
                parsed = parse_public_result_page(
                    html, query=batch.expression, limit=limit
                )
            except PageContractChanged as exc:
                return {
                    "index": batch.index,
                    "status": SearchStatus.PAGE_CONTRACT_CHANGED.value,
                    "detail": str(exc),
                }
            return {
                "index": batch.index,
                "status": SearchStatus.SUCCESS.value,
                "total_rows": parsed.total_rows,
                "excluded_non_journal_rows": parsed.excluded_non_journal_rows,
                "records": parsed.records,
                "incomplete_records": parsed.incomplete_records,
            }

        def reached_limit(results: list[dict[str, Any]]) -> bool:
            unique = _merge_candidate_records(
                record
                for item in results
                for record in item.get("records", ())
            )
            return len(unique) >= limit

        schedule = await run_batches(batches, execute, on_challenge=self.on_challenge,
                                     checkpoint=self.checkpoint, throttle=self.throttle,
                                     should_stop=reached_limit)
        return self._merge(schedule, batches)

    def _merge(self, schedule: dict[str, Any], batches: list[ExpressionBatch]) -> dict[str, Any]:
        collected: list[PaperRecord] = []
        incomplete: list[PaperRecord] = []
        total_rows = excluded = 0
        for item in schedule["results"]:
            total_rows += item.get("total_rows", 0)
            excluded += item.get("excluded_non_journal_rows", 0)
            collected.extend(item.get("records", ()))
            incomplete.extend(item.get("incomplete_records", ()))

        records = _merge_candidate_records(collected)
        annotated = annotate_and_sort_records(records, catalog=self.catalog)
        stopped_result = schedule.get("stopped_result")
        terminal_status = schedule["terminal_status"]
        complete = schedule["complete"] and terminal_status is None
        if terminal_status is not None:
            status = (
                SearchStatus.PARTIAL.value
                if annotated
                else terminal_status
            )
        elif not annotated:
            status = (
                SearchStatus.NO_RESULTS.value
                if complete
                else SearchStatus.PARTIAL.value
            )
        else:
            status = (
                SearchStatus.SUCCESS.value
                if complete and not incomplete
                else SearchStatus.PARTIAL.value
            )
        result = {
            "ok": status in {
                SearchStatus.SUCCESS.value,
                SearchStatus.NO_RESULTS.value,
                SearchStatus.PARTIAL.value,
            },
            "mode": "webvpn",
            "status": status,
            "complete": complete,
            "batches_completed": schedule["batches_completed"],
            "batches_total": schedule["batches_total"],
            "stopped_at_batch": schedule["stopped_at_batch"],
            "limit_reached": schedule["limit_reached"],
            "terminal_status": terminal_status,
            # 显式暴露：本模式必须有人值守，调用方不得据此安排无人值守任务
            "human_intervention_required": schedule["human_intervention_required"],
            "expressions": [batch.expression for batch in batches],
            "total_rows": total_rows,
            "excluded_non_journal_rows": excluded,
            "records": [record.to_dict() for record in annotated],
            "incomplete_records": [record.to_dict() for record in incomplete],
        }
        if terminal_status is not None:
            terminal_detail = (
                stopped_result.get("detail")
                if stopped_result is not None
                else None
            )
            if (
                not terminal_detail
                and terminal_status == SearchStatus.PAGE_CONTRACT_CHANGED.value
            ):
                terminal_detail = "知网页面结构已变化"
            if terminal_detail:
                result["terminal_detail"] = terminal_detail
            if status == terminal_status and terminal_detail:
                result["detail"] = terminal_detail
        return result


def _record_key(record: PaperRecord) -> tuple[str, str, int | None]:
    return (
        " ".join(record.title.split()).casefold(),
        " ".join(record.journal_raw.split()).casefold(),
        record.publication_year,
    )


def _normalized_authors(record: PaperRecord) -> set[str]:
    authors = record.authors
    if (
        not isinstance(authors, Sequence)
        or isinstance(authors, (str, bytes, bytearray))
    ):
        return set()
    normalized: set[str] = set()
    for author in authors:
        if not isinstance(author, str):
            continue
        folded = unicodedata.normalize("NFKC", author).casefold()
        identity = "".join(
            character
            for character in folded
            if unicodedata.category(character)[0] in {"L", "N"}
        )
        if identity:
            normalized.add(identity)
    return normalized


def _record_completeness_score(record: PaperRecord) -> int:
    return sum(
        (
            bool(record.title.strip()),
            bool(record.journal_raw.strip()),
            is_verifiable_publication_year(record.publication_year),
            len(record.authors),
            bool(record.publication_date.strip()),
            record.citations is not None,
            record.downloads is not None,
        )
    )


def _merge_candidate_records(
    records: Iterable[PaperRecord],
) -> list[PaperRecord]:
    groups: dict[
        tuple[str, str, int | None],
        list[PaperRecord],
    ] = {}
    for record in records:
        groups.setdefault(_record_key(record), []).append(record)
    merged: list[PaperRecord] = []
    for group in groups.values():
        merged.extend(_merge_record_group(group))
    return merged


def _merge_record_group(records: list[PaperRecord]) -> list[PaperRecord]:
    authored = [
        (record, _normalized_authors(record))
        for record in records
        if _normalized_authors(record)
    ]
    missing = [
        record
        for record in records
        if not _normalized_authors(record)
    ]
    parents = list(range(len(authored)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    for left in range(len(authored)):
        for right in range(left + 1, len(authored)):
            if not authored[left][1].isdisjoint(authored[right][1]):
                union(left, right)

    components: dict[int, list[PaperRecord]] = {}
    for index, (record, _authors) in enumerate(authored):
        components.setdefault(find(index), []).append(record)

    if not components:
        return [_best_record(missing)] if missing else []
    if len(components) == 1:
        only = next(iter(components.values()))
        return [_best_record([*only, *missing])]

    selected = [_best_record(component) for component in components.values()]
    if missing:
        selected.append(_best_record(missing))
    return selected


def _best_record(records: list[PaperRecord]) -> PaperRecord:
    best = records[0]
    for record in records[1:]:
        if (
            _record_completeness_score(record)
            > _record_completeness_score(best)
        ):
            best = record
    return best


def build_group_plans(
    topic: str,
    group: str,
    *,
    catalog: Path = DEFAULT_CATALOG,
    max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[ExpressionBatch]:
    if group in SUPPORTED_GROUPS:
        return build_batches(
            topic,
            journals_by_group(group, catalog),
            year_from=year_from,
            year_to=year_to,
            max_chars=max_chars,
            source_category=(
                CSSCI_SOURCE_CATEGORY if group == ENVIRONMENT_CSSCI_GROUP else None
            ),
        )
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
    "CHINESE_ENVIRONMENT_TOP_GROUP",
    "CSSCI_SOURCE_CATEGORY",
    "ENVIRONMENT_CSSCI_GROUP",
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
