"""知网专业检索表达式构造。

语法依据知网《专业检索》官方说明（可检索字段、匹配运算符、逻辑运算符、比较运算符）：

- 字段：``SU`` 主题、``LY`` 文献来源、``TI`` 篇名、``AB`` 摘要、``KY`` 关键词、
  ``AU`` 作者、``FT`` 全文、``YE`` 出版年份、``CF`` 被引频次。
- 主题推荐用相关匹配 ``%=``；``LY`` 用精确匹配 ``=``。
- 逻辑运算符 ``AND`` / ``OR`` / ``NOT`` **前后必须有空格**，优先级用英文半角括号。
- 年份区间用 ``YE BETWEEN ('2020', '2026')``。

本模块只负责构造与分批，不触网、不解析结果，便于离线测试。
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# 知网专业检索输入框的实际可提交长度未见官方说明，需实测确定（见 README 的
# Phase 0 探针）。在测得真实上限前按保守值分批，宁可多发一次请求，也不要
# 让整条表达式被静默截断——截断后检索照常返回结果，但覆盖范围已经不对。
DEFAULT_MAX_EXPRESSION_CHARS = 1500

TOPIC_FIELD = "SU"
JOURNAL_FIELD = "LY"
RELEVANCE_OPERATOR = "%="
EXACT_OPERATOR = "="

_FULLWIDTH_TO_HALFWIDTH = {"（": "(", "）": ")", "［": "[", "］": "]", "　": " "}
_HALFWIDTH_TO_FULLWIDTH = {"(": "（", ")": "）", "[": "［", "]": "］"}


class ExpressionTooLong(ValueError):
    """单个期刊的条件本身就超过长度上限，无法通过分批解决。"""


def _to_halfwidth(value: str) -> str:
    return "".join(_FULLWIDTH_TO_HALFWIDTH.get(char, char) for char in value)


def _to_fullwidth(value: str) -> str:
    return "".join(_HALFWIDTH_TO_FULLWIDTH.get(char, char) for char in value)


def journal_name_variants(title: str) -> list[str]:
    """返回一本期刊在知网中可能的写法。

    ``LY=`` 是精确匹配，括号全半角写错会**静默返回空结果而不报错**，
    很容易被误读成"该刊没有相关文献"。目录里是 ``经济学(季刊)``（半角），
    CSSCI 原表里是 ``经济学（季刊）``（全角），两种都要覆盖。
    """
    normalized = unicodedata.normalize("NFKC", title).strip()
    variants = [title.strip(), normalized, _to_halfwidth(normalized), _to_fullwidth(normalized)]
    seen: list[str] = []
    for variant in variants:
        if variant and variant not in seen:
            seen.append(variant)
    return seen


def quote_value(value: str) -> str:
    """把检索值包进英文半角单引号。

    知网专业检索没有转义机制，值里含单引号会破坏表达式结构，只能拒绝。
    """
    text = value.strip()
    if not text:
        raise ValueError("检索值不能为空")
    if "'" in text:
        raise ValueError(f"检索值不能包含英文单引号：{value!r}")
    return f"'{text}'"


def journal_clause(titles: list[str]) -> str:
    """把若干期刊拼成 ``(LY='甲' OR LY='乙')``，自动展开全半角变体。"""
    if not titles:
        raise ValueError("期刊列表不能为空")
    terms: list[str] = []
    for title in titles:
        for variant in journal_name_variants(title):
            term = f"{JOURNAL_FIELD}{EXACT_OPERATOR}{quote_value(variant)}"
            if term not in terms:
                terms.append(term)
    return "(" + " OR ".join(terms) + ")"


def year_clause(year_from: int, year_to: int) -> str:
    if year_from > year_to:
        raise ValueError(f"起始年份 {year_from} 不能晚于结束年份 {year_to}")
    return f"YE BETWEEN ('{year_from}', '{year_to}')"


def build_expression(topic: str, journals: list[str], *,
                     year_from: int | None = None, year_to: int | None = None,
                     topic_field: str = TOPIC_FIELD) -> str:
    """构造一条完整的专业检索表达式。"""
    clauses = [f"{topic_field} {RELEVANCE_OPERATOR} {quote_value(topic)}", journal_clause(journals)]
    if year_from is not None and year_to is not None:
        clauses.append(year_clause(year_from, year_to))
    elif (year_from is None) != (year_to is None):
        raise ValueError("年份区间必须同时提供起止年份")
    return " AND ".join(clauses)


@dataclass(frozen=True, slots=True)
class ExpressionBatch:
    index: int
    total: int
    journals: tuple[str, ...]
    expression: str


def build_batches(topic: str, journals: list[str], *,
                  year_from: int | None = None, year_to: int | None = None,
                  max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS) -> list[ExpressionBatch]:
    """按字符上限把期刊集合切成多条表达式。

    只切 ``LY=`` 列表；主题与年份条件在每批中重复出现。
    """
    if not journals:
        raise ValueError("期刊列表不能为空")
    groups: list[list[str]] = []
    current: list[str] = []
    for title in journals:
        probe = current + [title]
        if len(build_expression(topic, probe, year_from=year_from, year_to=year_to)) <= max_chars:
            current = probe
            continue
        if not current:
            raise ExpressionTooLong(
                f"期刊 {title!r} 的条件本身已超过 {max_chars} 字符上限，分批无法解决"
            )
        groups.append(current)
        current = [title]
    if current:
        groups.append(current)
    return [
        ExpressionBatch(
            index=position,
            total=len(groups),
            journals=tuple(group),
            expression=build_expression(topic, group, year_from=year_from, year_to=year_to),
        )
        for position, group in enumerate(groups, start=1)
    ]


_EXPRESSION_FIELD = re.compile(r"\b(SU|LY|TI|AB|KY|AU|FI|RP|AF|FU|FT|CO|RF|CLC|DOI|CF|YE|TKA)\b")


def looks_like_expression(value: str) -> bool:
    """粗判一段文本是否为专业检索表达式，用于区分它与普通主题词。"""
    return bool(_EXPRESSION_FIELD.search(value)) and ("=" in value or "BETWEEN" in value)
