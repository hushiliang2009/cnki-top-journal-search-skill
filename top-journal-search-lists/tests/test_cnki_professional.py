import importlib
import sys
from pathlib import Path

import pytest

from cnki_search import professional


MCPB_ROOT = Path(__file__).resolve().parents[1] / "mcpb" / "src"


def _load_mcpb_professional():
    sys.modules.pop("cnki_search.professional", None)
    sys.modules.pop("cnki_search", None)
    sys.path.insert(0, str(MCPB_ROOT))
    return importlib.import_module("cnki_search.professional")


def test_topic_uses_relevance_operator_and_spaced_logical_operators() -> None:
    expression = professional.build_expression("数字经济", ["管理世界"])
    assert expression.startswith("SU %= '数字经济'")
    # 知网要求逻辑运算符前后有空格，否则表达式不被接受
    assert " AND " in expression
    assert "AND(" not in expression and ")AND" not in expression


def test_journal_clause_expands_full_and_half_width_parentheses() -> None:
    """LY= 是精确匹配，括号写错会静默返回空结果，两种写法都必须覆盖。"""
    clause = professional.journal_clause(["经济学(季刊)"])
    assert "LY='经济学(季刊)'" in clause
    assert "LY='经济学（季刊）'" in clause
    assert clause.startswith("(") and clause.endswith(")")
    assert " OR " in clause


def test_journal_variants_are_deduplicated_for_plain_names() -> None:
    assert professional.journal_name_variants("管理世界") == ["管理世界"]


def test_year_clause_uses_between_syntax() -> None:
    expression = professional.build_expression(
        "共同富裕", ["经济研究"], year_from=2020, year_to=2026
    )
    assert "YE BETWEEN ('2020', '2026')" in expression


def test_year_bounds_must_be_supplied_together_and_ordered() -> None:
    with pytest.raises(ValueError):
        professional.build_expression("主题", ["经济研究"], year_from=2020)
    with pytest.raises(ValueError):
        professional.build_expression("主题", ["经济研究"], year_from=2026, year_to=2020)


def test_single_quote_in_value_is_rejected_rather_than_escaped() -> None:
    """知网专业检索没有转义机制，含单引号的值只能拒绝。"""
    with pytest.raises(ValueError):
        professional.build_expression("it's", ["经济研究"])
    with pytest.raises(ValueError):
        professional.journal_clause(["a'b"])


def test_empty_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        professional.build_expression("   ", ["经济研究"])
    with pytest.raises(ValueError):
        professional.journal_clause([])


def test_batches_respect_character_budget_and_cover_every_journal() -> None:
    journals = [f"测试期刊{index:03d}" for index in range(120)]
    batches = professional.build_batches("数字经济", journals, max_chars=400)
    assert len(batches) > 1
    for batch in batches:
        assert len(batch.expression) <= 400
        assert batch.total == len(batches)
    covered = [title for batch in batches for title in batch.journals]
    assert covered == journals                      # 不重不漏，且保持顺序
    assert [batch.index for batch in batches] == list(range(1, len(batches) + 1))


def test_single_batch_when_everything_fits() -> None:
    batches = professional.build_batches("数字经济", ["管理世界", "经济研究"], max_chars=1500)
    assert len(batches) == 1 and batches[0].total == 1


def test_journal_too_long_for_budget_raises_instead_of_looping() -> None:
    with pytest.raises(professional.ExpressionTooLong):
        professional.build_batches("数字经济", ["期刊" * 200], max_chars=100)


def test_looks_like_expression_separates_expressions_from_plain_topics() -> None:
    assert professional.looks_like_expression("SU %= '数字经济' AND LY='管理世界'")
    assert professional.looks_like_expression("YE BETWEEN ('2020', '2026')")
    assert not professional.looks_like_expression("数字经济 全要素生产率")


def test_mcpb_copy_exposes_the_same_behaviour() -> None:
    module = _load_mcpb_professional()
    assert module.build_expression("数字经济", ["管理世界"]).startswith("SU %= '数字经济'")
    assert module.DEFAULT_MAX_EXPRESSION_CHARS == professional.DEFAULT_MAX_EXPRESSION_CHARS
