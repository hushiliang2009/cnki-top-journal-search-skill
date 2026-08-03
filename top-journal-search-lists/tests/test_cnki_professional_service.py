import asyncio
import json
from pathlib import Path

import pytest

from cnki_search import professional_service as service_module
from cnki_search.models import SearchStatus
from cnki_search.professional import ExpressionBatch, PlanExecutionResult, SourceCategorySpec
from cnki_search.professional_service import (
    CnkiProfessionalSearchService,
    preview_expressions,
)
from cnki_search.webvpn import BatchCheckpoint


RESULT_TEMPLATE = """
<table class="result-table-list"><tbody>
  <tr>
    <td class="name"><a>{title}</a></td>
    <td class="author"><a>张三</a></td>
    <td class="source"><a>{journal}</a></td>
    <td class="date">2025-03-11</td>
    <td class="data">期刊</td>
  </tr>
  <tr>
    <td class="name"><a>被排除的学位论文</a></td>
    <td class="author"><a>李四</a></td>
    <td class="source"><a>某大学</a></td>
    <td class="date">2025-04-01</td>
    <td class="data">学位论文</td>
  </tr>
</tbody></table>
"""


def _result_page(
    *,
    title: str,
    journal: str,
    authors: tuple[str, ...] = (),
    publication_date: str = "2025-03-11",
    citations: int | None = None,
    downloads: int | None = None,
) -> str:
    author_links = "".join(f"<a>{author}</a>" for author in authors)
    citation_text = "" if citations is None else str(citations)
    download_text = "" if downloads is None else str(downloads)
    return f"""
    <table class="result-table-list"><tbody>
      <tr>
        <td class="name"><a>{title}</a></td>
        <td class="author">{author_links}</td>
        <td class="source"><a>{journal}</a></td>
        <td class="date">{publication_date}</td>
        <td class="data">期刊</td>
        <td class="quote">{citation_text}</td>
        <td class="download">{download_text}</td>
      </tr>
    </tbody></table>
    """


def _executor(pages: list[tuple[str, str]], seen: list[ExpressionBatch] | None = None):
    """模拟生产执行器：返回 PlanExecutionResult，并如实带上分面已生效的证据。"""
    async def execute(plan: ExpressionBatch) -> PlanExecutionResult:
        if seen is not None:
            seen.append(plan)
        title, journal = pages.pop(0)
        return PlanExecutionResult(
            status=SearchStatus.SUCCESS.value,
            html=RESULT_TEMPLATE.format(title=title, journal=journal),
            url="https://webvpn.example.edu.cn/https/abc/kns8s/defaultresult/index",
            source_category_applied=plan.source_category is not None,
            source_category_total=None,
        )
    return execute


def _tuple_executor(pages: list[tuple[str, str]]):
    """旧式三元组执行器：没有分面证据，服务只能保守认定分面未生效。"""
    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        title, journal = pages[0] if len(pages) == 1 else pages.pop(0)
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title=title, journal=journal),
                "https://webvpn.example.edu.cn/https/abc/kns8s/defaultresult/index")
    return execute


def _field_of(expression: str) -> str:
    return expression.split(" ", 1)[0]


def _service_yielding_by_field(
    records_by_field: dict[str, list[tuple[str, str]]],
) -> tuple[CnkiProfessionalSearchService, list[ExpressionBatch]]:
    seen: list[ExpressionBatch] = []

    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        seen.append(plan)
        html = "".join(
            _result_page(title=title, journal=journal)
            for title, journal in records_by_field.get(_field_of(plan.expression), [])
        )
        return SearchStatus.SUCCESS.value, html, "https://example.invalid/"

    return CnkiProfessionalSearchService(execute), seen


def _service_with_terminal_by_field(
    successful: dict[str, list[tuple[str, str]]],
    terminal_field: str,
    terminal_status: SearchStatus,
) -> tuple[CnkiProfessionalSearchService, list[ExpressionBatch]]:
    seen: list[ExpressionBatch] = []

    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        seen.append(plan)
        if _field_of(plan.expression) == terminal_field:
            return terminal_status.value, "", "https://example.invalid/"
        html = "".join(
            _result_page(title=title, journal=journal)
            for title, journal in successful.get(_field_of(plan.expression), [])
        )
        return SearchStatus.SUCCESS.value, html, "https://example.invalid/"

    return CnkiProfessionalSearchService(execute), seen


def test_chinese_top_plan_uses_exact_journals_without_facet() -> None:
    plans = service_module.preview_plans("数字经济", service_module.CHINESE_TOP_GROUP)
    assert len(plans) == 1
    assert "LY='管理世界'" in plans[0].expression
    assert plans[0].source_category is None
    assert plans[0].page_size == 50


def test_cssci_plan_uses_one_topic_expression_and_result_facet() -> None:
    plans = service_module.preview_plans("数字化转型", service_module.CSSCI_GROUP)
    assert len(plans) == 1
    assert plans[0].expression == "TI %= '数字化转型'"
    assert "LY=" not in plans[0].expression
    assert plans[0].source_category == SourceCategorySpec("P0209", "CSSCI")
    assert plans[0].page_size == 50


def test_fields_accumulate_unique_eligible_records_until_limit() -> None:
    service, seen = _service_yielding_by_field(
        {
            "TI": [("甲", "管理世界")],
            "SU": [("甲", "管理世界"), ("乙", "管理世界")],
        }
    )

    result = asyncio.run(
        service.search_group("碳中和", service_module.CHINESE_TOP_GROUP, limit=2)
    )

    assert [record["title"] for record in result["records"]] == ["甲", "乙"]
    assert result["topic_fields_tried"] == ["TI", "SU"]
    assert [record["topic_match_field"] for record in result["records"]] == ["TI", "SU"]
    assert [_field_of(plan.expression) for plan in seen] == ["TI", "SU"]


def test_out_of_scope_rows_do_not_consume_limit() -> None:
    service, _seen = _service_yielding_by_field(
        {
            "TI": [
                ("近似刊物", "管理学报"),
                ("合格刊物", "管理世界"),
            ],
        }
    )

    result = asyncio.run(
        service.search_group("生态", service_module.CHINESE_TOP_GROUP, limit=1)
    )

    assert result["eligible_record_count"] == 1
    assert result["excluded_out_of_scope_count"] == 1
    assert result["records"][0]["journal_matched_title"] == "管理世界"
    assert result["records"][0]["title"] == "合格刊物"


def test_all_fields_short_return_accumulated_unique_records_not_largest_field() -> None:
    service, seen = _service_yielding_by_field(
        {
            "TI": [("甲", "管理世界")],
            "SU": [("乙", "管理世界")],
            "KY": [("甲", "管理世界"), ("丙", "管理世界")],
            "TKA": [("丁", "管理世界")],
        }
    )

    result = asyncio.run(
        service.search_group("碳中和", service_module.CHINESE_TOP_GROUP, limit=10)
    )

    assert [record["title"] for record in result["records"]] == ["甲", "乙", "丙", "丁"]
    assert result["topic_fields_tried"] == ["TI", "SU", "KY", "TKA"]
    assert [_field_of(plan.expression) for plan in seen] == ["TI", "SU", "KY", "TKA"]
    assert result["complete"] is False


@pytest.mark.parametrize(
    "terminal_status",
    [
        SearchStatus.CHALLENGE_DETECTED,
        SearchStatus.LOGIN_REQUIRED,
        SearchStatus.FORBIDDEN,
        SearchStatus.RATE_LIMITED,
        SearchStatus.PAGE_CONTRACT_CHANGED,
    ],
)
def test_blocking_field_keeps_qualified_partial_and_stops_later_fields(
    terminal_status: SearchStatus,
) -> None:
    service, seen = _service_with_terminal_by_field(
        successful={"TI": [("已取得", "管理世界")], "SU": []},
        terminal_field="SU",
        terminal_status=terminal_status,
    )

    result = asyncio.run(
        service.search_group("环境治理", service_module.CHINESE_TOP_GROUP, limit=10)
    )

    assert [record["title"] for record in result["records"]] == ["已取得"]
    assert result["status"] == SearchStatus.PARTIAL.value
    assert result["terminal_status"] == terminal_status.value
    assert result["human_intervention_required"] is True
    assert result["topic_fields_tried"] == ["TI", "SU"]
    assert [_field_of(plan.expression) for plan in seen] == ["TI", "SU"]


def test_generic_cssci_uses_topic_only_plus_result_facet() -> None:
    policy = service_module.build_group_policy(service_module.CSSCI_GROUP)
    plans = service_module.build_group_plans(
        "环境治理", policy=policy, topic_field="TI"
    )

    assert len(plans) == 1
    assert plans[0].expression == "TI %= '环境治理'"
    assert "CSSCI" not in plans[0].expression
    assert plans[0].source_category == SourceCategorySpec("P0209", "CSSCI")


def test_chinese_top_group_fits_one_batch_and_is_annotated_at_level_six() -> None:
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(
        _executor([("数字经济与全要素生产率", "管理世界")], seen))
    result = asyncio.run(service.search_group("数字经济", service_module.CHINESE_TOP_GROUP, limit=1))

    assert len(seen) == 1, "13 本顶刊必须单批完成"
    assert result["journal_count"] == 13
    assert seen[0].source_category is None
    assert result["batches_total"] == 1 and result["complete"] is True
    assert result["status"] == SearchStatus.SUCCESS.value
    record = result["records"][0]
    assert record["journal_raw"] == "管理世界"
    assert record["priority_level"] == 6
    assert record["priority_group"] == "chinese_top_journals"


def test_expression_restricts_journals_and_uses_official_syntax() -> None:
    expressions = preview_expressions("数字经济", service_module.CHINESE_TOP_GROUP)
    assert len(expressions) == 1
    expression = expressions[0]
    assert expression.startswith("TI %= '数字经济'")
    assert "LY='管理世界'" in expression and "LY='中国社会科学'" in expression
    assert " AND " in expression and " OR " in expression


def test_non_journal_rows_are_excluded_from_records() -> None:
    """只收中文学术期刊论文；解析层是页面设置之外的兜底。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "经济研究")]))
    result = asyncio.run(service.search_group("共同富裕", service_module.CHINESE_TOP_GROUP, limit=1))
    assert result["excluded_non_journal_rows"] == 1
    assert all(record["journal_raw"] != "某大学" for record in result["records"])


def test_only_chinese_priority_groups_are_accepted() -> None:
    service = CnkiProfessionalSearchService(_executor([]))
    for group in ("ssci", "scie", "ft50", "no_such_group"):
        with pytest.raises(ValueError, match="不支持分组"):
            asyncio.run(service.search_group("主题", group))


def test_cssci_group_uses_one_facet_plan() -> None:
    pages = [("论文甲", "管理评论"), ("论文乙", "财经研究")]
    seen: list[ExpressionBatch] = []

    async def execute(plan: ExpressionBatch) -> PlanExecutionResult:
        seen.append(plan)
        title, journal = pages[min(len(seen) - 1, len(pages) - 1)]
        return PlanExecutionResult(
            status=SearchStatus.SUCCESS.value,
            html=RESULT_TEMPLATE.format(title=title, journal=journal),
            url="https://example.invalid/",
            source_category_applied=plan.source_category is not None,
        )

    # 预算调小以强制分批，验证跨批次合并而非只取第一批
    service = CnkiProfessionalSearchService(execute, max_expression_chars=900)
    result = asyncio.run(service.search_group("数字化转型", service_module.CSSCI_GROUP, limit=1))

    assert result["journal_count"] is None
    assert result["source_category"] == "CSSCI"
    assert result["batches_total"] == 1
    assert len(seen) == result["batches_total"]
    assert seen[0].source_category == SourceCategorySpec("P0209", "CSSCI")
    assert "LY=" not in seen[0].expression
    assert all(record["priority_level"] == 9 for record in result["records"])


def test_duplicate_records_across_batches_are_merged_once() -> None:
    async def execute(batch: ExpressionBatch) -> PlanExecutionResult:
        return PlanExecutionResult(
            status=SearchStatus.SUCCESS.value,
            html=RESULT_TEMPLATE.format(title="同一篇论文", journal="管理评论"),
            url="https://example.invalid/",
            source_category_applied=batch.source_category is not None,
        )

    service = CnkiProfessionalSearchService(execute, max_expression_chars=900)
    result = asyncio.run(service.search_group("数字化转型", service_module.CSSCI_GROUP))
    titles = [record["title"] for record in result["records"]]
    assert titles.count("同一篇论文") == 1


def test_limit_stops_before_submitting_remaining_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = [
        ExpressionBatch(index, 3, (), f"SU %= '主题{index}'")
        for index in range(1, 4)
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )
    executor_calls: list[int] = []

    async def execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        executor_calls.append(batch.index)
        return (
            SearchStatus.SUCCESS.value,
            _result_page(
                title=f"论文{batch.index}",
                journal="管理世界",
                authors=("张三",),
            ),
            "https://example.invalid/result",
        )

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
            limit=1,
        )
    )

    assert result["limit_reached"] is True
    assert result["terminal_status"] is None
    assert result["batches_completed"] == 1
    assert executor_calls == [1]
    assert "result_url" not in result


def test_checkpoint_preserves_missing_seq_rank_and_limit_across_resume(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = [
        ExpressionBatch(index, 2, (), f"SU %= '主题{index}'")
        for index in range(1, 3)
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )
    state = tmp_path / "progress.json"
    first_calls: list[int] = []

    async def first_execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        first_calls.append(batch.index)
        return (
            SearchStatus.SUCCESS.value,
            _result_page(
                title="缺失序号的合法题录",
                journal="管理世界",
                authors=("张三",),
            ),
            "",
        )

    first = asyncio.run(
        CnkiProfessionalSearchService(
            first_execute,
            checkpoint=BatchCheckpoint(state),
        ).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
            limit=1,
        )
    )

    assert first_calls == [1]
    assert first["limit_reached"] is True
    assert first["terminal_status"] is None
    assert first["records"][0]["result_rank"] == 0
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert saved["completed"]["1"]["records"][0]["result_rank"] == 0

    resumed_calls: list[int] = []

    async def resumed_execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        resumed_calls.append(batch.index)
        return (SearchStatus.NETWORK_ERROR.value, "", "")

    resumed = asyncio.run(
        CnkiProfessionalSearchService(
            resumed_execute,
            checkpoint=BatchCheckpoint(state),
        ).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
            limit=1,
        )
    )

    assert resumed_calls == []
    assert resumed["limit_reached"] is True
    assert resumed["terminal_status"] is None
    assert len(resumed["records"]) == 1
    assert resumed["records"][0]["result_rank"] == 0


def test_limit_counts_normalized_unique_formal_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = [
        ExpressionBatch(index, 3, (), f"SU %= '主题{index}'")
        for index in range(1, 4)
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )
    executor_calls: list[int] = []

    async def execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        executor_calls.append(batch.index)
        if batch.index == 1:
            html = (
                _result_page(title="Alpha Study", journal="管理世界")
                + _result_page(title="alpha study", journal="管理世界")
            )
        else:
            html = _result_page(title="Beta Study", journal="管理世界")
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
            limit=2,
        )
    )

    assert executor_calls == [1, 2]
    assert result["limit_reached"] is True
    assert result["batches_completed"] == 2
    assert len(result["records"]) == 2


def test_duplicate_keeps_more_complete_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = [
        ExpressionBatch(index, 2, (), f"SU %= '主题{index}'")
        for index in range(1, 3)
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )

    async def execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        if batch.index == 1:
            html = _result_page(
                title="Digital Economy Study",
                journal="管理世界",
            )
        else:
            html = _result_page(
                title=" digital economy study ",
                journal="管理世界",
                authors=("张三",),
                citations=8,
                downloads=12,
            )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
        )
    )

    assert len(result["records"]) == 1
    assert result["records"][0]["authors"] == ["张三"]
    assert result["records"][0]["citations"] == 8
    assert result["records"][0]["downloads"] == 12


def test_disjoint_authors_keep_same_title_journal_year_as_distinct_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = [
        ExpressionBatch(index, 3, (), f"SU %= '主题{index}'")
        for index in range(1, 4)
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )
    executor_calls: list[int] = []

    async def execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        executor_calls.append(batch.index)
        if batch.index == 1:
            html = (
                _result_page(
                    title="同名论文",
                    journal="管理世界",
                    authors=("张三",),
                )
                + _result_page(
                    title="同名论文",
                    journal="管理世界",
                    authors=("李四",),
                )
            )
        else:
            html = _result_page(
                title=f"后续论文{batch.index}",
                journal="经济研究",
                authors=("王五",),
            )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
            limit=2,
        )
    )

    assert executor_calls == [1]
    assert result["limit_reached"] is True
    assert len(result["records"]) == 2
    assert {tuple(record["authors"]) for record in result["records"]} == {
        ("张三",),
        ("李四",),
    }


@pytest.mark.parametrize(
    ("first_authors", "second_authors"),
    [
        (
            ("Zhang San", "李四"),
            ("李四", "ＺＨＡＮＧ　Ｓａｎ"),
        ),
        (
            ("张三", "李四"),
            ("李四", "王五"),
        ),
    ],
    ids=["normalized_order", "partial_overlap"],
)
def test_overlapping_authors_merge_candidate_duplicates(
    monkeypatch: pytest.MonkeyPatch,
    first_authors: tuple[str, ...],
    second_authors: tuple[str, ...],
) -> None:
    batches = [
        ExpressionBatch(index, 2, (), f"SU %= '主题{index}'")
        for index in range(1, 3)
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )

    async def execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        authors = first_authors if batch.index == 1 else second_authors
        html = _result_page(
            title="Same Study",
            journal="管理世界",
            authors=authors,
            citations=9 if batch.index == 2 else None,
        )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
        )
    )

    assert len(result["records"]) == 1
    assert result["records"][0]["citations"] == 9


@pytest.mark.parametrize(
    "author_order",
    [
        (("张三",), (), ("李四",)),
        ((), ("李四",), ("张三",)),
        (("李四",), ("张三",), ()),
    ],
    ids=["authored_missing_authored", "missing_authored_authored", "authored_authored_missing"],
)
def test_missing_authors_never_bridge_disjoint_author_components(
    monkeypatch: pytest.MonkeyPatch,
    author_order: tuple[tuple[str, ...], ...],
) -> None:
    batch = ExpressionBatch(1, 1, (), "SU %= '数字经济'")
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: [batch],
    )

    async def execute(_batch: ExpressionBatch) -> tuple[str, str, str]:
        html = "".join(
            _result_page(
                title="同名论文",
                journal="管理世界",
                authors=authors,
                citations=index,
            )
            for index, authors in enumerate(author_order, start=1)
        )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
            limit=3,
        )
    )

    assert result["limit_reached"] is True
    assert len(result["records"]) == 3
    assert {tuple(record["authors"]) for record in result["records"]} == {
        ("张三",),
        ("李四",),
        (),
    }


def test_common_author_punctuation_normalizes_to_one_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = [
        ExpressionBatch(index, 2, (), f"SU %= '主题{index}'")
        for index in range(1, 3)
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )

    async def execute(batch: ExpressionBatch) -> tuple[str, str, str]:
        author = "Zhang San" if batch.index == 1 else "Ｚｈａｎｇ-San"
        html = _result_page(
            title="Same Study",
            journal="管理世界",
            authors=(author,),
            citations=9 if batch.index == 2 else None,
        )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "数字经济",
            service_module.CHINESE_TOP_GROUP,
        )
    )

    assert len(result["records"]) == 1
    assert result["records"][0]["citations"] == 9


def test_challenge_without_handler_reports_partial_and_flags_human_intervention() -> None:
    async def execute(_batch: ExpressionBatch) -> tuple[str, str, str]:
        return (SearchStatus.CHALLENGE_DETECTED.value, "", "https://kns.cnki.net/verify/home")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(service.search_group("数字经济", service_module.CHINESE_TOP_GROUP))
    assert result["complete"] is False
    assert result["human_intervention_required"] is True
    assert result["stopped_at_batch"] == 1
    assert result["records"] == []
    assert result["status"] == SearchStatus.CHALLENGE_DETECTED.value
    assert result["terminal_status"] == SearchStatus.CHALLENGE_DETECTED.value
    assert result["limit_reached"] is False


def test_page_contract_status_stays_an_error_instead_of_becoming_no_results() -> None:
    async def execute(_plan: ExpressionBatch) -> tuple[str, str, str]:
        return (SearchStatus.PAGE_CONTRACT_CHANGED.value, "", "")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(
        service.search_group("数字经济", service_module.CHINESE_TOP_GROUP)
    )

    assert result["ok"] is False
    assert result["status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result["complete"] is False
    assert result["stopped_at_batch"] == 1
    assert result["records"] == []
    assert result["terminal_status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result["terminal_detail"] == "知网页面结构已变化"


def test_page_contract_after_valid_batch_returns_partial_with_stop_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batches = [
        ExpressionBatch(1, 2, ("管理世界",), "SU %= '数字经济' AND LY='管理世界'"),
        ExpressionBatch(2, 2, ("经济研究",), "SU %= '数字经济' AND LY='经济研究'"),
    ]
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: batches,
    )

    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        if plan.index == 1:
            return (
                SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(
                    title="数字经济与全要素生产率",
                    journal="管理世界",
                ),
                "",
            )
        return (SearchStatus.PAGE_CONTRACT_CHANGED.value, "", "")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(
        service.search_group("数字经济", service_module.CHINESE_TOP_GROUP)
    )

    assert result["ok"] is True
    assert result["status"] == SearchStatus.PARTIAL.value
    assert result["complete"] is False
    assert result["batches_completed"] == 1
    assert result["stopped_at_batch"] == 2
    assert [record["title"] for record in result["records"]] == [
        "数字经济与全要素生产率"
    ]
    assert result["terminal_status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result["terminal_detail"] == "知网页面结构已变化"


def test_parser_contract_exception_becomes_structured_page_contract_error() -> None:
    async def execute(_plan: ExpressionBatch) -> tuple[str, str, str]:
        malformed = "<table class='result-table-list'><tbody></tbody></table>"
        return (SearchStatus.SUCCESS.value, malformed, "")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(
        service.search_group("数字经济", service_module.CHINESE_TOP_GROUP)
    )

    assert result["ok"] is False
    assert result["status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result["complete"] is False
    assert "未解析出任何题录" in result["detail"]
    assert result["terminal_status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert "未解析出任何题录" in result["terminal_detail"]


def test_result_always_exposes_the_human_attendance_flag() -> None:
    """调用方据此判断能否安排无人值守任务，字段不得缺失。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "经济研究")]))
    result = asyncio.run(service.search_group("主题", service_module.CHINESE_TOP_GROUP, limit=1))
    assert "human_intervention_required" in result
    assert result["mode"] == "webvpn"


def test_custom_expression_runs_without_batching() -> None:
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(_executor([("某文", "经济研究")], seen))
    expression = "SU %= '碳中和' AND LY='经济研究' AND YE BETWEEN ('2020', '2026')"
    result = asyncio.run(service.search_expression(expression))
    assert [plan.expression for plan in seen] == [expression]
    assert result["batches_total"] == 1 and result["expressions"] == [expression]


PROFESSIONAL_RESULT_KEYS = (
    "source_category_requested",
    "source_category_applied",
    "source_category_total",
    "source_category_code",
    "topic_fields_tried",
    "eligible_record_count",
    "excluded_out_of_scope_count",
    "excluded_out_of_scope_records",
    "already_covered_higher_priority_count",
    "already_covered_higher_priority_records",
    "first_page_only",
    "complete",
    "human_intervention_required",
)


def test_professional_result_exposes_field_facet_and_scope_counts() -> None:
    """诊断字段必须恒定存在；缺字段会让调用方把"没筛过"误读成"筛过且为空"。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "管理世界")]))
    result = asyncio.run(service.search_group("主题", service_module.CHINESE_TOP_GROUP, limit=1))

    for key in PROFESSIONAL_RESULT_KEYS:
        assert key in result, key
    assert result["source_category_requested"] is None
    assert result["source_category_code"] is None
    assert result["source_category_applied"] is False
    assert result["source_category_total"] is None
    assert result["already_covered_higher_priority_count"] == 0
    assert result["already_covered_higher_priority_records"] == []
    assert result["first_page_only"] is True


def test_faceted_group_reports_its_requested_source_category() -> None:
    service = CnkiProfessionalSearchService(_executor([("某文", "管理世界")]))
    result = asyncio.run(service.search_group("主题", service_module.CSSCI_GROUP, limit=1))

    assert result["source_category_requested"] == "CSSCI"
    assert result["source_category_code"] == "P0209"


def test_custom_expression_reports_no_field_ladder_and_no_facet() -> None:
    """使用者自备表达式原样单次执行，不套字段阶梯也不加分面。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "管理世界")]))
    result = asyncio.run(service.search_expression("TI %= '主题'", limit=1))

    for key in PROFESSIONAL_RESULT_KEYS:
        assert key in result, key
    assert result["topic_fields_tried"] == []
    assert result["source_category_requested"] is None
    assert result["source_category_code"] is None
    assert result["source_category_applied"] is False


def test_legacy_tuple_executor_never_claims_an_unverified_facet() -> None:
    """三元组执行器拿不到分面证据，只能保守上报未生效。"""
    service = CnkiProfessionalSearchService(_tuple_executor([("某文", "管理世界")]))
    result = asyncio.run(service.search_group("主题", service_module.CSSCI_GROUP, limit=1))

    assert result["source_category_applied"] is False
    # 分面未经证实 => 结果页来源类别筛选的分组不得产出任何"合格"记录。
    assert result["records"] == []


def test_empty_batch_results_never_claim_the_facet_was_applied() -> None:
    """断点持久化失败等路径会把 results 清空；all([]) 为真会凭空上报已筛选。"""
    async def execute(_plan: ExpressionBatch) -> PlanExecutionResult:
        return PlanExecutionResult(
            status=SearchStatus.CONFIGURATION_ERROR.value,
            html="",
            url="",
            source_category_applied=False,
        )

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(service.search_group("主题", service_module.CSSCI_GROUP, limit=1))

    assert result["source_category_applied"] is False
    assert result["records"] == []


def test_facet_evidence_requires_every_batch_to_confirm_it() -> None:
    """只要有一个批次没证实分面，整组就不得上报已筛选。"""
    seen: list[int] = []

    async def execute(plan: ExpressionBatch) -> PlanExecutionResult:
        seen.append(plan.index)
        return PlanExecutionResult(
            status=SearchStatus.SUCCESS.value,
            html=RESULT_TEMPLATE.format(title="某文", journal="管理世界"),
            url="https://example.invalid/",
            source_category_applied=len(seen) > 1,
        )

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(service.search_group("主题", service_module.CSSCI_GROUP, limit=1))

    assert result["source_category_applied"] is False


def test_abandoned_first_batch_challenge_never_claims_the_facet() -> None:
    """首批即遭安全验证且人工放弃：一批未跑完，不得声称分面已生效。"""
    async def execute(_plan: ExpressionBatch) -> PlanExecutionResult:
        return PlanExecutionResult(
            status=SearchStatus.CHALLENGE_DETECTED.value,
            html="",
            url="",
            source_category_applied=False,
        )

    async def give_up(_plan: ExpressionBatch) -> bool:
        return False

    service = CnkiProfessionalSearchService(execute, on_challenge=give_up)
    result = asyncio.run(service.search_group("主题", service_module.CSSCI_GROUP, limit=1))

    assert result["source_category_applied"] is False
    assert result["human_intervention_required"] is True
    assert result["records"] == []
