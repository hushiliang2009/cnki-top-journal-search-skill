import asyncio

import pytest

from cnki_search import professional_service as service_module
from cnki_search.models import SearchStatus
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


def _executor(pages: list[tuple[str, str]], seen: list[str] | None = None):
    async def execute(expression: str) -> tuple[str, str, str]:
        if seen is not None:
            seen.append(expression)
        title, journal = pages.pop(0)
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title=title, journal=journal),
                "https://webvpn.example.edu.cn/https/abc/kns8s/defaultresult/index")
    return execute


def test_chinese_top_group_fits_one_batch_and_is_annotated_at_level_six() -> None:
    seen: list[str] = []
    service = CnkiProfessionalSearchService(
        _executor([("数字经济与全要素生产率", "管理世界")], seen))
    result = asyncio.run(service.search_group("数字经济", service_module.CHINESE_TOP_GROUP))

    assert len(seen) == 1, "13 本顶刊必须单批完成"
    assert result["journal_count"] == 13
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


def test_cssci_group_is_split_into_multiple_batches_and_merged() -> None:
    pages = [("论文甲", "管理评论"), ("论文乙", "财经研究")]
    seen: list[str] = []

    async def execute(expression: str) -> tuple[str, str, str]:
        seen.append(expression)
        title, journal = pages[min(len(seen) - 1, len(pages) - 1)]
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title=title, journal=journal), "https://example.invalid/")

    # 预算调小以强制分批，验证跨批次合并而非只取第一批
    service = CnkiProfessionalSearchService(execute, max_expression_chars=900)
    result = asyncio.run(service.search_group("数字化转型", service_module.CSSCI_GROUP))

    assert result["journal_count"] == 661
    assert result["batches_total"] > 1
    assert len(seen) == result["batches_total"]
    assert all(record["priority_level"] == 9 for record in result["records"])


def test_duplicate_records_across_batches_are_merged_once() -> None:
    async def execute(_expression: str) -> tuple[str, str, str]:
        return (SearchStatus.SUCCESS.value,
                RESULT_TEMPLATE.format(title="同一篇论文", journal="管理评论"),
                "https://example.invalid/")

    service = CnkiProfessionalSearchService(execute, max_expression_chars=900)
    result = asyncio.run(service.search_group("数字化转型", service_module.CSSCI_GROUP))
    titles = [record["title"] for record in result["records"]]
    assert titles.count("同一篇论文") == 1


def test_challenge_without_handler_reports_partial_and_flags_human_intervention() -> None:
    async def execute(_expression: str) -> tuple[str, str, str]:
        return (SearchStatus.CHALLENGE_DETECTED.value, "", "https://kns.cnki.net/verify/home")

    service = CnkiProfessionalSearchService(execute)
    result = asyncio.run(service.search_group("数字经济", service_module.CHINESE_TOP_GROUP))
    assert result["complete"] is False
    assert result["human_intervention_required"] is True
    assert result["stopped_at_batch"] == 1
    assert result["records"] == []
    assert result["status"] == SearchStatus.PARTIAL.value


def test_result_always_exposes_the_human_attendance_flag() -> None:
    """调用方据此判断能否安排无人值守任务，字段不得缺失。"""
    service = CnkiProfessionalSearchService(_executor([("某文", "经济研究")]))
    result = asyncio.run(service.search_group("主题", service_module.CHINESE_TOP_GROUP))
    assert "human_intervention_required" in result
    assert result["mode"] == "webvpn"


def test_custom_expression_runs_without_batching() -> None:
    seen: list[str] = []
    service = CnkiProfessionalSearchService(_executor([("某文", "经济研究")], seen))
    expression = "SU %= '碳中和' AND LY='经济研究' AND YE BETWEEN ('2020', '2026')"
    result = asyncio.run(service.search_expression(expression))
    assert seen == [expression]
    assert result["batches_total"] == 1 and result["expressions"] == [expression]
