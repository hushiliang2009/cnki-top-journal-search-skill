"""知网专业检索表达式构造（环境版）。

语法依据知网专业检索页面列出的可检索字段：

- ``SU`` 主题、``TKA`` 篇关摘、``TI`` 篇名、``KY`` 关键词、``AB`` 摘要、
  ``CO`` 小标题、``FT`` 全文、``AU`` 作者、``FI`` 第一作者、``RP`` 通讯作者、
  ``AF`` 作者单位、``LY`` 期刊名称、``RF`` 参考文献、``FU`` 基金、
  ``CLC`` 中图分类号、``SN`` ISSN、``CN`` CN、``DOI`` DOI、
  ``QKLM`` 栏目信息、``FAF`` 第一单位、``CF`` 被引频次。
- 主题推荐用相关匹配 ``%=``；``LY`` 用精确匹配 ``=``。
- 逻辑运算符 ``AND`` / ``OR`` / ``NOT`` **前后必须有空格**，优先级用英文半角括号。
- ``YE`` 不是可检索字段；年份必须通过页面的出版年度起止控件设置。

本模块只负责构造与分批，不触网、不解析结果，便于离线测试。

本文件是通用版 ``cnki_search.professional`` 的独立移植，不导入通用版包：两个产品
各自发布、各自安装，任何跨包导入都会让其中一个的安装状态影响另一个。移植意味着
通用版的修正不会自动到达这里，改动时必须两边对照。
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping

from .models import MAX_RESULTS_PER_PAGE

# 输入框的 maxlength 属性是 18000，但**服务端接受的上限远低于此**。
# 2026-07-28 在知网实机夹逼（主题固定为"数字经济"，逐档提交 CSSCI 刊名前 N 本）：
#
#     50 本 / 1161 字符 → 成功        200 本 / 4393 字符 → 暂无数据
#    150 本 / 2905 字符 → 成功        250 本 / 5284 字符 → 暂无数据
#    175 本 / 3633 字符 → 成功        300 本 / 6129 字符 → 暂无数据
#    （661 本 / 12940 字符 → 暂无数据）
#
# 即真实分界落在 3633 与 4393 之间。这里取 3000，留约 17% 余量。
# 上表约束的是**字符数**，与刊名属于哪个学科无关，因此同样适用于环境目录。
# 超限时站点返回「抱歉，暂无数据，请稍后重试。」而不是报错，很容易被误读成
# "该主题在这些期刊上没有文献"——所以宁可多分一批，也不要贴着上限走。
DEFAULT_MAX_EXPRESSION_CHARS = 3000

SEARCHABLE_FIELDS: Mapping[str, str] = MappingProxyType({
    "SU": "主题", "TKA": "篇关摘", "TI": "篇名", "KY": "关键词",
    "AB": "摘要", "CO": "小标题", "FT": "全文", "AU": "作者",
    "FI": "第一作者", "RP": "通讯作者", "AF": "作者单位",
    "LY": "期刊名称", "RF": "参考文献", "FU": "基金",
    "CLC": "中图分类号", "SN": "ISSN", "CN": "CN", "DOI": "DOI",
    "QKLM": "栏目信息", "FAF": "第一单位", "CF": "被引频次",
})

TOPIC_FIELD_PRIORITY: tuple[str, ...] = ("TI", "SU", "KY", "TKA")
TOPIC_FIELD = TOPIC_FIELD_PRIORITY[0]
JOURNAL_FIELD = "LY"
RELEVANCE_OPERATOR = "%="
EXACT_OPERATOR = "="

_FULLWIDTH_TO_HALFWIDTH = {"（": "(", "）": ")", "［": "[", "］": "]", "　": " "}
_HALFWIDTH_TO_FULLWIDTH = {"(": "（", ")": "）", "[": "［", "]": "］"}


class ExpressionTooLong(ValueError):
    """单个期刊的条件本身就超过长度上限，无法通过分批解决。"""


def validate_topic_field(value: str) -> str:
    if value not in TOPIC_FIELD_PRIORITY:
        raise ValueError("检索字段只允许 TI、SU、KY、TKA")
    return value


@dataclass(frozen=True, slots=True)
class SourceCategorySpec:
    code: Literal["P0209", "P01"]
    label: Literal["CSSCI", "北大核心"]

    def __post_init__(self) -> None:
        if (self.code, self.label) not in {
            ("P0209", "CSSCI"),
            ("P01", "北大核心"),
        }:
            raise ValueError("来源类别代码与名称不匹配")


def validate_source_category(
    value: SourceCategorySpec | None,
) -> SourceCategorySpec | None:
    if value is not None and not isinstance(value, SourceCategorySpec):
        raise ValueError("来源类别必须使用受控代码与名称")
    return value


@dataclass(frozen=True, slots=True)
class SearchGroupPolicy:
    scope_id: str
    catalog_version: str
    journal_selector: Literal["exact_titles", "topic_only"]
    source_category: SourceCategorySpec | None
    journal_titles: tuple[str, ...]
    eligible_journal_ids: frozenset[str]
    eligible_priority_levels: frozenset[int]
    required_index_membership: str | None
    result_filter: Literal["matched_title", "matched_journal_id", "source_category"]


@dataclass(frozen=True, slots=True)
class PlanExecutionResult:
    status: str
    html: str
    url: str
    source_category_applied: bool = False
    source_category_total: int | None = None


def _to_halfwidth(value: str) -> str:
    return "".join(_FULLWIDTH_TO_HALFWIDTH.get(char, char) for char in value)


def _to_fullwidth(value: str) -> str:
    return "".join(_HALFWIDTH_TO_FULLWIDTH.get(char, char) for char in value)


def journal_name_variants(title: str) -> list[str]:
    """返回一本期刊在知网中可能的写法。

    ``LY=`` 是精确匹配，括号全半角写错会**静默返回空结果而不报错**，
    很容易被误读成"该刊没有相关文献"。环境目录里有 ``中国人口·资源与环境(英文版)``
    这类带括号的刊名，来源表中常写成全角 ``（英文版）``，两种都要覆盖。
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


def validate_year_range(
    year_from: int | None, year_to: int | None,
) -> tuple[int | None, int | None]:
    if (year_from is None) != (year_to is None):
        raise ValueError("年份区间必须同时提供起止年份")
    if year_from is None:
        return None, None
    if year_from > year_to:
        raise ValueError(f"起始年份 {year_from} 不能晚于结束年份 {year_to}")
    return year_from, year_to


def build_topic_expression(
    topic: str,
    *,
    year_from: int | None = None,
    year_to: int | None = None,
    topic_field: str = TOPIC_FIELD,
) -> str:
    field = validate_topic_field(topic_field)
    validate_year_range(year_from, year_to)
    return f"{field} {RELEVANCE_OPERATOR} {quote_value(topic)}"


def build_expression(topic: str, journals: list[str], *,
                     year_from: int | None = None, year_to: int | None = None,
                     topic_field: str = TOPIC_FIELD) -> str:
    """构造一条完整的专业检索表达式。"""
    field = validate_topic_field(topic_field)
    validate_year_range(year_from, year_to)
    return " AND ".join(
        [f"{field} {RELEVANCE_OPERATOR} {quote_value(topic)}", journal_clause(journals)]
    )


@dataclass(frozen=True, slots=True)
class ExpressionBatch:
    index: int
    total: int
    journals: tuple[str, ...]
    expression: str
    page_size: int = MAX_RESULTS_PER_PAGE
    scope_id: str = ""
    catalog_version: str = ""
    topic_field: str | None = None
    source_category: SourceCategorySpec | None = None
    year_from: int | None = None
    year_to: int | None = None


def build_batches(topic: str, journals: list[str], *,
                  year_from: int | None = None, year_to: int | None = None,
                  max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
                  source_category: SourceCategorySpec | None = None,
                  topic_field: str = TOPIC_FIELD,
                  scope_id: str = "",
                  catalog_version: str = "") -> list[ExpressionBatch]:
    """按字符上限把期刊集合切成多条表达式。

    只切 ``LY=`` 列表。年份与来源类别作为批次元数据交给页面条件控件，
    绝不写入专业检索表达式。
    """
    if not journals:
        raise ValueError("期刊列表不能为空")
    category = validate_source_category(source_category)
    groups: list[list[str]] = []
    current: list[str] = []
    for title in journals:
        probe = current + [title]
        probe_expression = build_expression(
            topic, probe, year_from=year_from, year_to=year_to, topic_field=topic_field
        )
        if len(probe_expression) <= max_chars:
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
            expression=build_expression(
                topic, group, year_from=year_from, year_to=year_to, topic_field=topic_field
            ),
            scope_id=scope_id,
            catalog_version=catalog_version,
            topic_field=topic_field,
            source_category=category,
            year_from=year_from,
            year_to=year_to,
        )
        for position, group in enumerate(groups, start=1)
    ]


_EXPRESSION_FIELD_TOKEN = re.compile(
    r"\b([A-Z][A-Z0-9]*)\s*(?:%=|>=|<=|=|>|<|\bBETWEEN\b)"
)


def validate_expression_fields(value: str) -> tuple[str, ...]:
    """核对表达式中所有字段，防止合法字段掩盖 ``YE`` 等非法字段。"""
    fields = tuple(_EXPRESSION_FIELD_TOKEN.findall(value))
    if not fields:
        raise ValueError("未识别到专业检索字段")
    unsupported = tuple(dict.fromkeys(field for field in fields if field not in SEARCHABLE_FIELDS))
    if unsupported:
        raise ValueError(f"专业检索不支持字段：{', '.join(unsupported)}")
    return fields


def looks_like_expression(value: str) -> bool:
    """粗判一段文本是否为专业检索表达式，用于区分它与普通主题词。"""
    try:
        validate_expression_fields(value)
    except ValueError:
        return False
    return True
