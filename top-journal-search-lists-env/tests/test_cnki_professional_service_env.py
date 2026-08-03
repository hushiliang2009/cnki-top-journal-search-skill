import asyncio
import json
from collections import Counter
from pathlib import Path

import pytest

from cnki_search_env import professional_service as service_module
from cnki_search_env.catalog_adapter import DEFAULT_CATALOG, lookup_journals
from cnki_search_env.models import SearchStatus
from cnki_search_env.professional import ExpressionBatch, SourceCategorySpec
from cnki_search_env.professional_service import (
    CnkiProfessionalSearchService,
    preview_expressions,
)
from cnki_search_env.webvpn import BatchCheckpoint


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
    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        if seen is not None:
            seen.append(plan)
        # 字段升级会多轮执行同一批次，用尽即抛 IndexError 与被测行为无关
        title, journal = pages[0] if len(pages) == 1 else pages.pop(0)
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title=title, journal=journal),
                "https://webvpn.example.edu.cn/https/abc/kns8s/defaultresult/index")
    return execute


def test_chinese_environment_top_plan_uses_exact_journals_without_facet() -> None:
    plans = service_module.preview_plans(
        "大气污染治理", service_module.CHINESE_ENVIRONMENT_TOP_GROUP)
    assert len(plans) == 1
    assert "LY='中国环境科学'" in plans[0].expression
    assert plans[0].source_category is None
    assert plans[0].page_size == 50


def test_environment_cssci_plan_enumerates_journals_and_keeps_the_facet() -> None:
    """环境 CSSCI 只是 CSSCI 的子集，分面收不窄到环境学科，必须同时枚举刊名。"""
    plans = service_module.preview_plans("碳中和", service_module.ENVIRONMENT_CSSCI_GROUP)
    assert len(plans) > 1, "241 本刊装不进一条表达式，必须分批"
    for plan in plans:
        assert plan.expression.startswith("TI %= '碳中和'"), "默认字段是优先级最高的 TI"
        assert "LY=" in plan.expression
        assert len(plan.expression) <= service_module.DEFAULT_MAX_EXPRESSION_CHARS
        assert plan.source_category == "CSSCI", "每一批都要带来源类别，不能只给第一批"
        assert plan.page_size == 50
    # 字段可指定：升级逻辑正是靠它逐级替换检索式
    fallback = service_module.preview_plans(
        "碳中和", service_module.ENVIRONMENT_CSSCI_GROUP, topic_field="SU")
    assert all(p.expression.startswith("SU %= '碳中和'") for p in fallback)
    covered = [title for plan in plans for title in plan.journals]
    assert len(covered) == len(set(covered)) == 241


def test_chinese_top_group_fits_one_batch_and_is_annotated_at_level_six() -> None:
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(
        _executor([("大气污染的协同治理", "中国环境科学")], seen))
    result = asyncio.run(
        service.search_group(
            "大气污染治理", service_module.CHINESE_ENVIRONMENT_TOP_GROUP, limit=1))

    assert len(seen) == 1, "6 本环境顶刊必须单批完成，且 TI 够用即停"
    assert result["journal_count"] == 6
    assert seen[0].source_category is None
    assert result["batches_total"] == 1 and result["complete"] is True
    assert result["status"] == SearchStatus.SUCCESS.value
    record = result["records"][0]
    assert record["journal_raw"] == "中国环境科学"
    assert record["priority_level"] == 6
    assert record["priority_group"] == "chinese_environment_top"


def test_expression_restricts_journals_and_uses_official_syntax() -> None:
    expressions = preview_expressions(
        "大气污染治理", service_module.CHINESE_ENVIRONMENT_TOP_GROUP)
    assert len(expressions) == 1
    expression = expressions[0]
    assert expression.startswith("TI %= '大气污染治理'")
    assert "LY='中国环境科学'" in expression and "LY='环境科学学报'" in expression
    assert " AND " in expression and " OR " in expression


def test_non_journal_rows_are_excluded_from_records() -> None:
    """只收中文学术期刊论文；解析层是页面设置之外的兜底。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "环境科学学报")]))
    result = asyncio.run(service.search_group(
        "碳排放", service_module.CHINESE_ENVIRONMENT_TOP_GROUP, limit=1))
    assert result["excluded_non_journal_rows"] == 1
    assert all(record["journal_raw"] != "某大学" for record in result["records"])


def test_only_chinese_priority_groups_are_accepted() -> None:
    service = CnkiProfessionalSearchService(_executor([]))
    for group in ("environment_ssci", "environment_scie",
                  "comprehensive_super_journals", "no_such_group"):
        with pytest.raises(ValueError, match="只覆盖中文层级"):
            asyncio.run(service.search_group("主题", group))


def test_environment_cssci_group_merges_across_every_batch() -> None:
    pages = [("论文甲", "农业经济问题"), ("论文乙", "生态文明研究")]
    seen: list[ExpressionBatch] = []

    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        seen.append(plan)
        title, journal = pages[min(len(seen) - 1, len(pages) - 1)]
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title=title, journal=journal), "https://example.invalid/")

    # 预算调小以强制多分批，验证跨批次合并而非只取第一批
    service = CnkiProfessionalSearchService(execute, max_expression_chars=900)
    result = asyncio.run(
        service.search_group("碳中和", service_module.ENVIRONMENT_CSSCI_GROUP, limit=50))

    assert result["journal_count"] == 241
    assert result["source_category"] == "CSSCI"
    assert result["batches_total"] > 1
    per_field = Counter(_field_of(plan.expression) for plan in seen)
    assert per_field[result["topic_field"]] == result["batches_total"], "每一批都要真的提交"
    assert list(per_field) == result["topic_fields_tried"], "字段必须按声明的优先序试"
    assert all(plan.source_category == "CSSCI" for plan in seen)
    assert all("LY=" in plan.expression for plan in seen)
    assert all(record["priority_level"] == 9 for record in result["records"])


def test_duplicate_records_across_batches_are_merged_once() -> None:
    async def execute(_batch: ExpressionBatch) -> tuple[str, str, str]:
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title="同一篇论文", journal="生态学报"),
                "https://example.invalid/")

    service = CnkiProfessionalSearchService(execute, max_expression_chars=900)
    result = asyncio.run(service.search_group("碳中和", service_module.ENVIRONMENT_CSSCI_GROUP))
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
                journal="环境科学学报",
                authors=("张三",),
            ),
            "https://example.invalid/result",
        )

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
                journal="环境科学学报",
                authors=("张三",),
            ),
            "",
        )

    first = asyncio.run(
        CnkiProfessionalSearchService(
            first_execute,
            checkpoint=BatchCheckpoint(state),
        ).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
                _result_page(title="Alpha Study", journal="Journal A")
                + _result_page(title="alpha study", journal="journal a")
            )
        else:
            html = _result_page(title="Beta Study", journal="Journal B")
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
                journal="Management World",
            )
        else:
            html = _result_page(
                title=" digital economy study ",
                journal="management world",
                authors=("张三",),
                citations=8,
                downloads=12,
            )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
                    journal="环境科学学报",
                    authors=("张三",),
                )
                + _result_page(
                    title="同名论文",
                    journal="环境科学学报",
                    authors=("李四",),
                )
            )
        else:
            html = _result_page(
                title=f"后续论文{batch.index}",
                journal="环境科学研究",
                authors=("王五",),
            )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
            journal="Journal A",
            authors=authors,
            citations=9 if batch.index == 2 else None,
        )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
    batch = ExpressionBatch(1, 1, (), "SU %= '大气污染治理'")
    monkeypatch.setattr(
        service_module,
        "build_group_plans",
        lambda *_args, **_kwargs: [batch],
    )

    async def execute(_batch: ExpressionBatch) -> tuple[str, str, str]:
        html = "".join(
            _result_page(
                title="同名论文",
                journal="环境科学学报",
                authors=authors,
                citations=index,
            )
            for index, authors in enumerate(author_order, start=1)
        )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
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
            journal="Journal A",
            authors=(author,),
            citations=9 if batch.index == 2 else None,
        )
        return (SearchStatus.SUCCESS.value, html, "")

    result = asyncio.run(
        CnkiProfessionalSearchService(execute).search_group(
            "大气污染治理",
            service_module.CHINESE_ENVIRONMENT_TOP_GROUP,
        )
    )

    assert len(result["records"]) == 1
    assert result["records"][0]["citations"] == 9


def test_challenge_without_handler_reports_partial_and_flags_human_intervention() -> None:
    async def execute(_batch: ExpressionBatch) -> tuple[str, str, str]:
        return (SearchStatus.CHALLENGE_DETECTED.value, "", "https://kns.cnki.net/verify/home")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(service.search_group("大气污染治理", service_module.CHINESE_ENVIRONMENT_TOP_GROUP))
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
        service.search_group("大气污染治理", service_module.CHINESE_ENVIRONMENT_TOP_GROUP)
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
        ExpressionBatch(1, 2, ("环境科学学报",), "SU %= '大气污染治理' AND LY='管理世界'"),
        ExpressionBatch(2, 2, ("环境科学研究",), "SU %= '大气污染治理' AND LY='经济研究'"),
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
                    title="大气污染的协同治理",
                    journal="环境科学学报",
                ),
                "",
            )
        return (SearchStatus.PAGE_CONTRACT_CHANGED.value, "", "")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(
        service.search_group("大气污染治理", service_module.CHINESE_ENVIRONMENT_TOP_GROUP)
    )

    assert result["ok"] is True
    assert result["status"] == SearchStatus.PARTIAL.value
    assert result["complete"] is False
    assert result["batches_completed"] == 1
    assert result["stopped_at_batch"] == 2
    assert [record["title"] for record in result["records"]] == [
        "大气污染的协同治理"
    ]
    assert result["terminal_status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result["terminal_detail"] == "知网页面结构已变化"


def test_parser_contract_exception_becomes_structured_page_contract_error() -> None:
    async def execute(_plan: ExpressionBatch) -> tuple[str, str, str]:
        malformed = "<table class='result-table-list'><tbody></tbody></table>"
        return (SearchStatus.SUCCESS.value, malformed, "")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(
        service.search_group("大气污染治理", service_module.CHINESE_ENVIRONMENT_TOP_GROUP)
    )

    assert result["ok"] is False
    assert result["status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result["complete"] is False
    assert "未解析出任何题录" in result["detail"]
    assert result["terminal_status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert "未解析出任何题录" in result["terminal_detail"]


def test_result_always_exposes_the_human_attendance_flag() -> None:
    """调用方据此判断能否安排无人值守任务，字段不得缺失。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "环境科学研究")]))
    result = asyncio.run(service.search_group("主题", service_module.CHINESE_ENVIRONMENT_TOP_GROUP))
    assert "human_intervention_required" in result
    assert result["mode"] == "webvpn"


def test_custom_expression_runs_without_batching() -> None:
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(_executor([("某文", "环境科学研究")], seen))
    expression = "SU %= '碳中和' AND LY='经济研究' AND YE BETWEEN ('2020', '2026')"
    result = asyncio.run(service.search_expression(expression))
    assert [plan.expression for plan in seen] == [expression]
    assert result["batches_total"] == 1 and result["expressions"] == [expression]


# ── 检索字段按优先序升级（TI → SU → KY → TKA） ─────────────────────────

def _field_of(expression: str) -> str:
    return expression.split(" ", 1)[0]


def _executor_yielding(counts: dict[str, int], seen: list[ExpressionBatch]):
    """按字段返回不同数量的题录，用于驱动升级判定。"""
    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        seen.append(plan)
        rows = "".join(
            f"<tr><td class='name'><a>文{index}</a></td>"
            f"<td class='author'><a>张三</a></td>"
            f"<td class='source'><a>环境科学</a></td>"
            f"<td class='date'>2025-03-11</td><td class='data'>期刊</td></tr>"
            for index in range(counts.get(_field_of(plan.expression), 0))
        )
        return (SearchStatus.SUCCESS.value,
                f"<table class='result-table-list'><tbody>{rows}</tbody></table>",
                "https://example.invalid/")
    return execute


def test_title_field_is_tried_first() -> None:
    """TI 优先：够用时不再向后试，省下的是限流预算与风控暴露。"""
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(_executor_yielding({"TI": 5}, seen))
    result = asyncio.run(service.search_group(
        "碳中和", service_module.CHINESE_ENVIRONMENT_TOP_GROUP, limit=5))
    assert [_field_of(p.expression) for p in seen] == ["TI"]
    assert result["topic_field"] == "TI"
    assert result["record_count"] if "record_count" in result else len(result["records"]) == 5


def test_fields_escalate_in_declared_order_until_enough() -> None:
    """TI 不够就退到 SU，再不够 KY，最后 TKA——顺序固定，不是随机试。"""
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(
        _executor_yielding({"TI": 1, "SU": 2, "KY": 9}, seen))
    result = asyncio.run(service.search_group(
        "碳中和", service_module.CHINESE_ENVIRONMENT_TOP_GROUP, limit=9))
    assert [_field_of(p.expression) for p in seen] == ["TI", "SU", "KY"]
    assert result["topic_field"] == "KY"
    assert result["topic_fields_tried"] == ["TI", "SU", "KY"]
    assert len(result["records"]) == 9


def test_best_field_wins_when_none_reaches_the_limit() -> None:
    """都不够用时取有效记录最多的那个，而不是最后试的那个。"""
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(
        _executor_yielding({"TI": 1, "SU": 7, "KY": 2, "TKA": 3}, seen))
    result = asyncio.run(service.search_group(
        "碳中和", service_module.CHINESE_ENVIRONMENT_TOP_GROUP, limit=50))
    assert [_field_of(p.expression) for p in seen] == ["TI", "SU", "KY", "TKA"]
    assert result["topic_field"] == "SU"
    assert len(result["records"]) == 7


def test_escalation_stops_immediately_on_a_blocking_status() -> None:
    """命中风控后不得继续换字段试探——那正是把账号推向更严限制的做法。"""
    seen: list[ExpressionBatch] = []

    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        seen.append(plan)
        return (SearchStatus.CHALLENGE_DETECTED.value, "", "https://example.invalid/")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(service.search_group(
        "碳中和", service_module.CHINESE_ENVIRONMENT_TOP_GROUP, limit=50))
    assert [_field_of(p.expression) for p in seen] == ["TI"]
    assert result["terminal_status"] == SearchStatus.CHALLENGE_DETECTED.value


def test_declared_priority_is_the_documented_one() -> None:
    assert service_module.TOPIC_FIELD_PRIORITY == ("TI", "SU", "KY", "TKA")


@pytest.mark.parametrize(
    ("group", "journal_count", "selector", "facet"),
    [
        ("chinese_environment_top", 6, "exact_titles", None),
        ("other_formally_recognized_chinese", 60, "exact_titles", None),
        (
            "environment_cssci",
            241,
            "exact_titles",
            SourceCategorySpec("P0209", "CSSCI"),
        ),
        (
            "pku_core",
            1987,
            "topic_only",
            SourceCategorySpec("P01", "北大核心"),
        ),
    ],
)
def test_environment_policies_come_from_catalog(
    group: str,
    journal_count: int,
    selector: str,
    facet: SourceCategorySpec | None,
) -> None:
    """目录范围变动时，策略必须由 cnki_scope 的固定载荷重新生成。"""
    policy = service_module.build_group_policy(group)
    assert policy.journal_selector == selector
    assert len(policy.eligible_journal_ids) == journal_count
    assert policy.source_category == facet


def test_pku_core_has_no_ly_and_accepts_members_at_levels_1_to_12() -> None:
    """北大核心应仅按主题检索，再由受控分面和目录身份过滤。"""
    policy = service_module.build_group_policy("pku_core")
    plan = service_module.build_group_plans(
        "气候治理", policy=policy, topic_field="TI"
    )[0]
    assert plan.expression == "TI %= '气候治理'"
    assert "LY=" not in plan.expression
    assert policy.eligible_priority_levels == frozenset(range(1, 13))


def test_every_environment_cssci_batch_keeps_exact_titles_and_cssci_facet() -> None:
    """CSSCI 分面不能代替环境目录中的逐刊限定。"""
    policy = service_module.build_group_policy("environment_cssci")
    plans = service_module.build_group_plans(
        "环境政策", policy=policy, topic_field="TI"
    )
    assert len(plans) > 1
    assert all("LY=" in plan.expression for plan in plans)
    assert all(
        plan.source_category == SourceCategorySpec("P0209", "CSSCI")
        for plan in plans
    )


def test_pku_core_direct_scope_and_skill_supplement_bases_are_fixed() -> None:
    """单组 MCP 直接检索使用完整北大核心成员，而非跨组补集。"""
    policy = service_module.build_group_policy("pku_core")
    matches = lookup_journals(DEFAULT_CATALOG, list(policy.journal_titles))
    higher = sum(1 for item in matches if 1 <= item["priority_level"] <= 10)
    supplement = sum(1 for item in matches if item["priority_level"] in {11, 12})
    assert len(policy.eligible_journal_ids) == 1987
    assert higher == 245
    assert supplement == 1742
    assert higher + supplement == 1987


def test_environment_cssci_excludes_non_level_nine_before_limit() -> None:
    """目录外的第七级记录不能抢占环境 CSSCI 的单组限额。"""
    async def execute(_plan: ExpressionBatch) -> tuple[str, str, str]:
        rows = "".join(
            (
                "<tr><td class='name'><a>第七级</a></td>"
                "<td class='author'><a>张三</a></td>"
                "<td class='source'><a>中国人口·资源与环境</a></td>"
                "<td class='date'>2025-03-11</td><td class='data'>期刊</td></tr>",
                "<tr><td class='name'><a>第九级</a></td>"
                "<td class='author'><a>李四</a></td>"
                "<td class='source'><a>上海经济研究</a></td>"
                "<td class='date'>2025-03-11</td><td class='data'>期刊</td></tr>",
            )
        )
        return (
            SearchStatus.SUCCESS.value,
            f"<table class='result-table-list'><tbody>{rows}</tbody></table>",
            "https://example.invalid/",
        )

    result = asyncio.run(CnkiProfessionalSearchService(execute).search_group(
        "环境政策", "environment_cssci", limit=1,
    ))
    assert [item["priority_level"] for item in result["records"]] == [9]
    assert result["excluded_out_of_scope_count"] == 1
