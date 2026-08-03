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

from catalog_lookup import DEFAULT_CATALOG, journals_by_group, validate_catalog

from .models import PaperRecord, SearchStatus, is_verifiable_publication_year
from .professional import (
    DEFAULT_MAX_EXPRESSION_CHARS,
    ExpressionBatch,
    PlanExecutionResult,
    SearchGroupPolicy,
    SourceCategorySpec,
    TOPIC_FIELD_PRIORITY,
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
    detail: str | None = None


@dataclass(slots=True)
class FieldOutcome:
    topic_field: str
    eligible_records: list[PaperRecord]
    excluded_records: list[PaperRecord]
    incomplete_records: list[PaperRecord]
    terminal_status: str | None
    terminal_detail: str | None
    human_intervention_required: bool
    source_category_applied: bool
    source_category_total: int | None
    batches_completed: int
    batches_total: int
    stopped_at_batch: int | None
    total_rows: int
    excluded_non_journal_rows: int


#: 页面驱动：接收完整执行计划，返回 ``(status, html, url)``。
#: 真实实现驱动浏览器；测试注入假实现即可完全离线。
ExpressionExecutor = Callable[
    [ExpressionBatch],
    Awaitable[tuple[str, str, str] | PlanExecutionResult],
]


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
        return await self._search_group_fields(
            topic, group, limit=limit, year_from=year_from, year_to=year_to
        )

    async def _search_group_fields(
        self,
        topic: str,
        group: str,
        *,
        limit: int,
        year_from: int | None,
        year_to: int | None,
    ) -> dict[str, Any]:
        if not 1 <= limit <= 50:
            raise ValueError("返回数量必须在 1 至 50 之间")
        policy = build_group_policy(group, catalog=self.catalog)
        eligible: list[PaperRecord] = []
        excluded: list[PaperRecord] = []
        incomplete: list[PaperRecord] = []
        fields_tried: list[str] = []
        terminal_status: str | None = None
        terminal_detail: str | None = None
        human_intervention_required = False
        # 分面证据取合取：任一字段或批次未证实，整组都不得声称已筛选。
        source_category_applied = policy.source_category is not None
        source_category_total: int | None = None
        batches_completed = batches_total = total_rows = excluded_non_journal_rows = 0
        stopped_at_batch: int | None = None

        for topic_field in TOPIC_FIELD_PRIORITY:
            fields_tried.append(topic_field)
            batches = build_group_plans(
                topic,
                policy=policy,
                topic_field=topic_field,
                max_chars=self.max_expression_chars,
                year_from=year_from,
                year_to=year_to,
            )
            outcome = await self._run_field(
                batches,
                policy=policy,
                remaining_limit=limit - len(eligible),
            )
            eligible = _merge_candidate_records([*eligible, *outcome.eligible_records])
            excluded = _merge_candidate_records([*excluded, *outcome.excluded_records])
            incomplete = _merge_candidate_records([*incomplete, *outcome.incomplete_records])
            eligible = annotate_and_sort_records(eligible, catalog=self.catalog)[:limit]
            batches_completed += outcome.batches_completed
            batches_total += outcome.batches_total
            total_rows += outcome.total_rows
            excluded_non_journal_rows += outcome.excluded_non_journal_rows
            stopped_at_batch = outcome.stopped_at_batch
            source_category_applied &= outcome.source_category_applied
            if outcome.source_category_total is not None:
                source_category_total = outcome.source_category_total
            human_intervention_required |= outcome.human_intervention_required
            if outcome.terminal_status is not None:
                terminal_status = outcome.terminal_status
                terminal_detail = outcome.terminal_detail
                human_intervention_required = True
                break
            if len(eligible) >= limit:
                break

        complete = terminal_status is None and len(eligible) >= limit
        if terminal_status is not None:
            status = SearchStatus.PARTIAL.value if eligible else terminal_status
        elif not eligible:
            status = SearchStatus.NO_RESULTS.value if complete else SearchStatus.PARTIAL.value
        else:
            status = SearchStatus.SUCCESS.value if complete and not incomplete else SearchStatus.PARTIAL.value
        result = {
            "ok": status in {SearchStatus.SUCCESS.value, SearchStatus.NO_RESULTS.value, SearchStatus.PARTIAL.value},
            "mode": "webvpn",
            "status": status,
            "complete": complete,
            "group": group,
            "journal_count": len(policy.journal_titles) if policy.journal_selector == "exact_titles" else None,
            "source_category": policy.source_category.label if policy.source_category else None,
            "source_category_requested": (
                policy.source_category.label if policy.source_category else None
            ),
            "source_category_code": (
                policy.source_category.code if policy.source_category else None
            ),
            "source_category_applied": source_category_applied,
            "source_category_total": source_category_total,
            "batches_completed": batches_completed,
            "batches_total": batches_total,
            "stopped_at_batch": stopped_at_batch,
            "limit_reached": len(eligible) >= limit,
            "terminal_status": terminal_status,
            "human_intervention_required": human_intervention_required,
            "expressions": [],
            "total_rows": total_rows,
            "excluded_non_journal_rows": excluded_non_journal_rows,
            "eligible_record_count": len(eligible),
            "excluded_out_of_scope_count": len(excluded),
            "excluded_out_of_scope_records": [record.to_dict() for record in excluded],
            "topic_fields_tried": fields_tried,
            "topic_field": fields_tried[-1],
            # 单组 MCP 调用没有 Skill 工作流中"已检索更高层级分组"的上下文，
            # 因此恒为空；字段仍必须存在，缺字段会被误读成"没有重复项"之外的含义。
            "already_covered_higher_priority_count": 0,
            "already_covered_higher_priority_records": [],
            "first_page_only": True,
            "records": [record.to_dict() for record in eligible],
            "incomplete_records": [record.to_dict() for record in incomplete],
        }
        if terminal_status is not None:
            detail = terminal_detail
            if not detail and terminal_status == SearchStatus.PAGE_CONTRACT_CHANGED.value:
                detail = "知网页面结构已变化"
            if detail:
                result["terminal_detail"] = detail
                if status == terminal_status:
                    result["detail"] = detail
        return result

    async def search_expression(self, expression: str, *, limit: int = 20) -> dict[str, Any]:
        """直接执行一条使用者自备的专业检索表达式，不做分批。"""
        batch = ExpressionBatch(index=1, total=1, journals=(), expression=expression)
        return await self._run([batch], limit)

    async def _run_field(
        self,
        batches: list[ExpressionBatch],
        *,
        policy: SearchGroupPolicy,
        remaining_limit: int,
    ) -> FieldOutcome:
        async def execute(batch: ExpressionBatch) -> dict[str, Any]:
            executed = await self.executor(batch)
            if isinstance(executed, PlanExecutionResult):
                status, html = executed.status, executed.html
                source_applied = executed.source_category_applied
                source_total = executed.source_category_total
            else:
                status, html, _url = executed
                # 三元组执行器不返回分面证据；乐观上报会把未筛选结果说成已筛选。
                source_applied = False
                source_total = None
            if status != SearchStatus.SUCCESS.value:
                return {
                    "index": batch.index,
                    "status": status,
                    "source_category_applied": source_applied,
                    "source_category_total": source_total,
                }
            try:
                parsed = parse_public_result_page(
                    html, query=batch.expression, limit=50
                )
            except PageContractChanged as exc:
                return {
                    "index": batch.index,
                    "status": SearchStatus.PAGE_CONTRACT_CHANGED.value,
                    "detail": str(exc),
                    "source_category_applied": source_applied,
                    "source_category_total": source_total,
                }
            for record in parsed.records:
                record.topic_match_field = batch.topic_field
                record.matched_topic_fields = [batch.topic_field] if batch.topic_field else []
                record.matched_search_groups = [policy.scope_id]
            return {
                "index": batch.index,
                "status": SearchStatus.SUCCESS.value,
                "total_rows": parsed.total_rows,
                "excluded_non_journal_rows": parsed.excluded_non_journal_rows,
                "records": parsed.records,
                "incomplete_records": parsed.incomplete_records,
                "source_category_applied": source_applied,
                "source_category_total": source_total,
            }

        def reached_limit(results: list[dict[str, Any]]) -> bool:
            records = _merge_candidate_records(
                record for item in results for record in item.get("records", ())
            )
            annotated = annotate_and_sort_records(records, catalog=self.catalog)
            source_applied = (
                bool(results)
                and all(item.get("source_category_applied", False) for item in results)
                if policy.source_category else False
            )
            qualified, _excluded = _partition_eligible(
                annotated, policy, source_category_applied=source_applied
            )
            return len(qualified) >= remaining_limit

        schedule = await run_batches(
            batches,
            execute,
            on_challenge=self.on_challenge,
            checkpoint=self.checkpoint,
            throttle=self.throttle,
            should_stop=reached_limit,
        )
        records = _merge_candidate_records(
            record
            for item in schedule["results"]
            for record in item.get("records", ())
        )
        annotated = annotate_and_sort_records(records, catalog=self.catalog)
        source_applied = (
            bool(schedule["results"])
            and all(item.get("source_category_applied", False)
                    for item in schedule["results"])
            if policy.source_category else False
        )
        eligible, excluded = _partition_eligible(
            annotated, policy, source_category_applied=source_applied
        )
        return FieldOutcome(
            topic_field=batches[0].topic_field or "",
            eligible_records=eligible,
            excluded_records=excluded,
            incomplete_records=[
                record
                for item in schedule["results"]
                for record in item.get("incomplete_records", ())
            ],
            terminal_status=schedule["terminal_status"],
            terminal_detail=(schedule.get("stopped_result") or {}).get("detail"),
            human_intervention_required=schedule["human_intervention_required"],
            source_category_applied=source_applied,
            source_category_total=next(
                (item["source_category_total"] for item in schedule["results"]
                 if item.get("source_category_total") is not None),
                None,
            ),
            batches_completed=schedule["batches_completed"],
            batches_total=schedule["batches_total"],
            stopped_at_batch=schedule["stopped_at_batch"],
            total_rows=sum(item.get("total_rows", 0) for item in schedule["results"]),
            excluded_non_journal_rows=sum(
                item.get("excluded_non_journal_rows", 0)
                for item in schedule["results"]
            ),
        )

    async def _run(self, batches: list[ExpressionBatch], limit: int) -> dict[str, Any]:
        async def execute(batch: ExpressionBatch) -> dict[str, Any]:
            # 生产执行器返回 PlanExecutionResult；只解三元组会在实机直接 TypeError。
            executed = await self.executor(batch)
            if isinstance(executed, PlanExecutionResult):
                status, html = executed.status, executed.html
            else:
                status, html, _url = executed
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
            # 自备表达式原样单次执行：不套 TI→SU→KY→TKA 阶梯，也不加来源类别分面。
            # 诊断字段仍恒定存在，调用方无需按调用形式分支解析。
            "topic_fields_tried": [],
            "source_category_requested": None,
            "source_category_code": None,
            "source_category_applied": False,
            "source_category_total": None,
            "eligible_record_count": len(annotated),
            "excluded_out_of_scope_count": 0,
            "excluded_out_of_scope_records": [],
            "already_covered_higher_priority_count": 0,
            "already_covered_higher_priority_records": [],
            "first_page_only": True,
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


def _record_identity(record: PaperRecord) -> tuple[object, ...]:
    return (
        "metadata",
        " ".join(record.title.split()).casefold(),
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
        tuple[object, ...],
        list[PaperRecord],
    ] = {}
    for record in records:
        groups.setdefault(_record_identity(record), []).append(record)
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
    topic_fields = _ordered_metadata(
        records,
        "matched_topic_fields",
        TOPIC_FIELD_PRIORITY,
    )
    groups = _ordered_metadata(
        records,
        "matched_search_groups",
        (),
    )
    first_field = next(
        (record.topic_match_field for record in records if record.topic_match_field),
        None,
    )
    best.topic_match_field = first_field
    best.matched_topic_fields = topic_fields
    best.matched_search_groups = groups
    return best


def _ordered_metadata(
    records: Iterable[PaperRecord],
    attribute: str,
    declared_order: Sequence[str],
) -> list[str]:
    encountered: list[str] = []
    for record in records:
        for value in getattr(record, attribute):
            if value and value not in encountered:
                encountered.append(value)
    if not declared_order:
        return encountered
    return [value for value in declared_order if value in encountered] + [
        value for value in encountered if value not in declared_order
    ]


def build_group_policy(
    group: str,
    *,
    catalog: Path = DEFAULT_CATALOG,
) -> SearchGroupPolicy:
    catalog_version = validate_catalog(catalog)["catalog_version"]
    if group == CHINESE_TOP_GROUP:
        titles = tuple(journals_by_group(group, catalog))
        return SearchGroupPolicy(
            group,
            catalog_version,
            "exact_titles",
            None,
            titles,
            frozenset(),
            frozenset({6}),
            None,
            "matched_title",
        )
    if group == CSSCI_GROUP:
        return SearchGroupPolicy(
            group,
            catalog_version,
            "topic_only",
            SourceCategorySpec("P0209", "CSSCI"),
            (),
            frozenset(),
            frozenset(),
            "CSSCI",
            "source_category",
        )
    raise ValueError(f"CNKI 专业检索不支持分组 {group!r}")


def _partition_eligible(
    records: Iterable[PaperRecord],
    policy: SearchGroupPolicy,
    *,
    source_category_applied: bool,
) -> tuple[list[PaperRecord], list[PaperRecord]]:
    eligible: list[PaperRecord] = []
    excluded: list[PaperRecord] = []
    for record in records:
        if policy.result_filter == "matched_title":
            matched = record.journal_matched_title in policy.journal_titles
        else:
            matched = source_category_applied
        (eligible if matched else excluded).append(record)
    return eligible, excluded


def build_group_plans(
    topic: str,
    group: str | None = None,
    *,
    policy: SearchGroupPolicy | None = None,
    catalog: Path = DEFAULT_CATALOG,
    max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
    year_from: int | None = None,
    year_to: int | None = None,
    topic_field: str = "TI",
) -> list[ExpressionBatch]:
    resolved_policy = policy or build_group_policy(group or "", catalog=catalog)
    if resolved_policy.journal_selector == "exact_titles":
        return build_batches(
            topic,
            list(resolved_policy.journal_titles),
            year_from=year_from,
            year_to=year_to,
            max_chars=max_chars,
            topic_field=topic_field,
            scope_id=resolved_policy.scope_id,
            catalog_version=resolved_policy.catalog_version,
        )
    return [
        ExpressionBatch(
            index=1,
            total=1,
            journals=(),
            expression=build_topic_expression(
                topic,
                year_from=year_from,
                year_to=year_to,
                topic_field=topic_field,
            ),
            scope_id=resolved_policy.scope_id,
            catalog_version=resolved_policy.catalog_version,
            topic_field=topic_field,
            source_category=resolved_policy.source_category,
        )
    ]


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
