import importlib
import sys
from pathlib import Path

import pytest

from cnki_search_env import professional


MCPB_ROOT = Path(__file__).resolve().parents[1] / "mcpb" / "src"


def _load_mcpb_professional():
    sys.modules.pop("cnki_search_env.professional", None)
    sys.modules.pop("cnki_search_env", None)
    sys.path.insert(0, str(MCPB_ROOT))
    return importlib.import_module("cnki_search_env.professional")


def test_topic_uses_relevance_operator_and_spaced_logical_operators() -> None:
    expression = professional.build_expression("大气污染治理", ["中国环境科学"])
    assert expression.startswith("TI %= '大气污染治理'")
    # 知网要求逻辑运算符前后有空格，否则表达式不被接受
    assert " AND " in expression
    assert "AND(" not in expression and ")AND" not in expression


def test_journal_clause_expands_full_and_half_width_parentheses() -> None:
    """LY= 是精确匹配，括号写错会静默返回空结果，两种写法都必须覆盖。"""
    clause = professional.journal_clause(["中国人口·资源与环境(英文版)"])
    assert "LY='中国人口·资源与环境(英文版)'" in clause
    assert "LY='中国人口·资源与环境（英文版）'" in clause
    assert clause.startswith("(") and clause.endswith(")")
    assert " OR " in clause


def test_journal_variants_are_deduplicated_for_plain_names() -> None:
    assert professional.journal_name_variants("环境科学学报") == ["环境科学学报"]


def test_year_clause_uses_between_syntax() -> None:
    expression = professional.build_expression(
        "碳中和", ["环境科学"], year_from=2020, year_to=2026
    )
    assert "YE BETWEEN ('2020', '2026')" in expression


def test_year_bounds_must_be_supplied_together_and_ordered() -> None:
    with pytest.raises(ValueError):
        professional.build_expression("主题", ["环境科学"], year_from=2020)
    with pytest.raises(ValueError):
        professional.build_expression("主题", ["环境科学"], year_from=2026, year_to=2020)


def test_single_quote_in_value_is_rejected_rather_than_escaped() -> None:
    """知网专业检索没有转义机制，含单引号的值只能拒绝。"""
    with pytest.raises(ValueError):
        professional.build_expression("it's", ["环境科学"])
    with pytest.raises(ValueError):
        professional.journal_clause(["a'b"])


def test_empty_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        professional.build_expression("   ", ["环境科学"])
    with pytest.raises(ValueError):
        professional.journal_clause([])


def test_batches_respect_character_budget_and_cover_every_journal() -> None:
    journals = [f"测试环境期刊{index:03d}" for index in range(120)]
    batches = professional.build_batches("大气污染", journals, max_chars=400)
    assert len(batches) > 1
    for batch in batches:
        assert len(batch.expression) <= 400
        assert batch.total == len(batches)
    covered = [title for batch in batches for title in batch.journals]
    assert covered == journals                      # 不重不漏，且保持顺序
    assert [batch.index for batch in batches] == list(range(1, len(batches) + 1))


def test_single_batch_when_everything_fits() -> None:
    batches = professional.build_batches("大气污染", ["中国环境科学", "环境科学"], max_chars=1500)
    assert len(batches) == 1 and batches[0].total == 1


def test_journal_too_long_for_budget_raises_instead_of_looping() -> None:
    with pytest.raises(professional.ExpressionTooLong):
        professional.build_batches("大气污染", ["期刊" * 200], max_chars=100)


def test_batches_carry_the_declared_source_category() -> None:
    """环境版 CSSCI 每批都要带来源类别；缺省时保持 None，不凭空加筛选。"""
    plain = professional.build_batches("碳排放", ["环境科学"])
    assert plain[0].source_category is None
    faceted = professional.build_batches("碳排放", ["环境科学"], source_category="CSSCI")
    assert [batch.source_category for batch in faceted] == ["CSSCI"]


def test_batch_page_size_defaults_to_site_ceiling() -> None:
    from cnki_search_env.models import MAX_RESULTS_PER_PAGE

    assert professional.build_batches("碳排放", ["环境科学"])[0].page_size == MAX_RESULTS_PER_PAGE


def test_looks_like_expression_separates_expressions_from_plain_topics() -> None:
    assert professional.looks_like_expression("SU %= '碳中和' AND LY='中国环境科学'")
    assert professional.looks_like_expression("YE BETWEEN ('2020', '2026')")
    assert not professional.looks_like_expression("大气污染 协同治理")


def test_expression_budget_stays_under_the_measured_server_limit() -> None:
    """实测服务端分界落在 3633 与 4393 字符之间，预算必须留在下界之内。"""
    assert professional.DEFAULT_MAX_EXPRESSION_CHARS <= 3633


def test_mcpb_copy_exposes_the_same_behaviour() -> None:
    module = _load_mcpb_professional()
    assert module.build_expression("碳中和", ["环境科学"]).startswith("TI %= '碳中和'")
    assert module.DEFAULT_MAX_EXPRESSION_CHARS == professional.DEFAULT_MAX_EXPRESSION_CHARS
    assert module.build_batches(
        "碳中和", ["环境科学"], source_category="CSSCI"
    )[0].source_category == "CSSCI"


def test_all_builders_default_to_title_and_reject_unknown_fields() -> None:
    assert professional.build_topic_expression("碳中和").startswith("TI %=")
    assert professional.build_expression("碳中和", ["环境科学"]).startswith("TI %=")
    assert professional.build_batches("碳中和", ["环境科学"])[0].topic_field == "TI"
    with pytest.raises(ValueError, match="TI、SU、KY、TKA"):
        professional.build_topic_expression("碳中和", topic_field="AB")


def test_source_category_is_a_closed_pair_not_free_text() -> None:
    spec = professional.SourceCategorySpec("P0209", "CSSCI")
    assert spec.code == "P0209"
    assert professional.SourceCategorySpec("P01", "北大核心").label == "北大核心"
    with pytest.raises(ValueError):
        professional.SourceCategorySpec("P01", "CSSCI")
