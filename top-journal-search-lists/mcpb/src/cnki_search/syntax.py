from __future__ import annotations

import re

from .fields import supported_field_codes


_FIELD_PATTERN = re.compile(r"\b([A-Za-z][A-Za-z0-9]{1,7})\s*=")


def _balanced_parentheses(text: str) -> bool:
    depth = 0
    quote: str | None = None
    for char in text:
        if char in {"'", '"'}:
            quote = None if quote == char else char if quote is None else quote
        elif quote is None and char == "(":
            depth += 1
        elif quote is None and char == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def validate_professional_expression(expression: str) -> list[str]:
    errors: list[str] = []
    if not expression.strip():
        return ["专业检索表达式不能为空"]
    if expression.count("'") % 2 or expression.count('"') % 2:
        errors.append("引号不配对")
    if not _balanced_parentheses(expression):
        errors.append("括号不配对")
    supported = supported_field_codes()
    unknown = sorted(
        {match.group(1).upper() for match in _FIELD_PATTERN.finditer(expression)} - supported
    )
    errors.extend(f"不支持字段代码: {code}" for code in unknown)
    return errors


def normalize_professional_expression(expression: str) -> str:
    return expression

