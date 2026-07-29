import asyncio

import pytest

from cnki_search import professional_service as service_module
from cnki_search.models import SearchStatus
from cnki_search.professional import ExpressionBatch
from cnki_search.professional_service import CnkiProfessionalSearchService, preview_expressions


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
        title, journal = pages.pop(0)
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title=title, journal=journal),
                "https://webvpn.example.edu.cn/https/abc/kns8s/defaultresult/index")
    return execute


def test_chinese_top_plan_uses_exact_journals_without_facet() -> None:
    plans = service_module.preview_plans("数字经济", service_module.CHINESE_TOP_GROUP)
    assert len(plans) == 1
    assert "LY='管理世界'" in plans[0].expression
    assert plans[0].source_category is None
    assert plans[0].page_size == 50


def test_cssci_plan_uses_one_topic_expression_and_result_facet() -> None:
    plans = service_module.preview_plans("数字化转型", service_module.CSSCI_GROUP)
    assert len(plans) == 1
    assert plans[0].expression == "SU %= '数字化转型'"
    assert "LY=" not in plans[0].expression
    assert plans[0].source_category == "CSSCI"
    assert plans[0].page_size == 50


def test_chinese_top_group_fits_one_batch_and_is_annotated_at_level_six() -> None:
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(
        _executor([("数字经济与全要素生产率", "管理世界")], seen))
    result = asyncio.run(service.search_group("数字经济", service_module.CHINESE_TOP_GROUP))

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
    assert expression.startswith("SU %= '数字经济'")
    assert "LY='管理世界'" in expression and "LY='中国社会科学'" in expression
    assert " AND " in expression and " OR " in expression


def test_non_journal_rows_are_excluded_from_records() -> None:
    """只收中文学术期刊论文；解析层是页面设置之外的兜底。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "经济研究")]))
    result = asyncio.run(service.search_group("共同富裕", service_module.CHINESE_TOP_GROUP))
    assert result["excluded_non_journal_rows"] == 1
    assert all(record["journal_raw"] != "某大学" for record in result["records"])


def test_only_chinese_priority_groups_are_accepted() -> None:
    service = CnkiProfessionalSearchService(_executor([]))
    for group in ("ssci", "scie", "ft50", "no_such_group"):
        with pytest.raises(ValueError, match="只覆盖中文层级"):
            asyncio.run(service.search_group("主题", group))


def test_cssci_group_uses_one_facet_plan() -> None:
    pages = [("论文甲", "管理评论"), ("论文乙", "财经研究")]
    seen: list[ExpressionBatch] = []

    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        seen.append(plan)
        title, journal = pages[min(len(seen) - 1, len(pages) - 1)]
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title=title, journal=journal), "https://example.invalid/")

    # 预算调小以强制分批，验证跨批次合并而非只取第一批
    service = CnkiProfessionalSearchService(execute, max_expression_chars=900)
    result = asyncio.run(service.search_group("数字化转型", service_module.CSSCI_GROUP))

    assert result["journal_count"] is None
    assert result["source_category"] == "CSSCI"
    assert result["batches_total"] == 1
    assert len(seen) == result["batches_total"]
    assert seen[0].source_category == "CSSCI"
    assert "LY=" not in seen[0].expression
    assert all(record["priority_level"] == 9 for record in result["records"])


def test_duplicate_records_across_batches_are_merged_once() -> None:
    async def execute(_batch: ExpressionBatch) -> tuple[str, str, str]:
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title="同一篇论文", journal="管理评论"),
                "https://example.invalid/")

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
            journal="Journal A",
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
    result = asyncio.run(service.search_group("主题", service_module.CHINESE_TOP_GROUP))
    assert "human_intervention_required" in result
    assert result["mode"] == "webvpn"


def test_custom_expression_runs_without_batching() -> None:
    seen: list[ExpressionBatch] = []
    service = CnkiProfessionalSearchService(_executor([("某文", "经济研究")], seen))
    expression = "SU %= '碳中和' AND LY='经济研究' AND YE BETWEEN ('2020', '2026')"
    result = asyncio.run(service.search_expression(expression))
    assert [plan.expression for plan in seen] == [expression]
    assert result["batches_total"] == 1 and result["expressions"] == [expression]
