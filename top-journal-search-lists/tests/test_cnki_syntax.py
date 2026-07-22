from cnki_search.syntax import normalize_professional_expression, validate_professional_expression


def test_professional_expression_is_not_rewritten() -> None:
    text = "SU='数字化转型' AND (KY='创新' OR TI='研发')"
    assert validate_professional_expression(text) == []
    assert normalize_professional_expression(text) == text


def test_professional_expression_reports_unbalanced_delimiters_and_unknown_field() -> None:
    errors = validate_professional_expression("BAD='创新' AND (SU='转型'")
    assert "括号不配对" in errors
    assert "不支持字段代码: BAD" in errors
