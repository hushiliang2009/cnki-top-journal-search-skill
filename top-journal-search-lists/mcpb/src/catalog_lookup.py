from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


CATALOG_FILENAME = "Academic_Journal_Master_Directory_20260715.md"


def _resolve_default_catalog() -> Path:
    """按实际布局定位综合期刊目录，兼容 Skill 与 MCPB 两种目录深度。

    Skill 布局：scripts/catalog_lookup.py → <root>/references/
    MCPB 布局：mcpb/src/catalog_lookup.py → mcpb/src/references/
    两者相差一层，固定深度推导必然有一种失败。
    """
    configured = os.environ.get("CNKI_CATALOG_PATH")
    if configured and Path(configured).is_file():
        return Path(configured)
    here = Path(__file__).resolve().parent
    for base in (here, here.parent):
        candidate = base / "references" / CATALOG_FILENAME
        if candidate.is_file():
            return candidate
    return here.parent / "references" / CATALOG_FILENAME


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = _resolve_default_catalog()
EXPECTED_GROUPS = [
    "economics_top5",
    "ncs_pnas",
    "utd24",
    "ft50",
    "field_top",
    "chinese_top_journals",
    "other_top_journals",
    "ssci",
    "cssci",
    "scie",
]
EXPECTED_SOURCES = [
    "NCS_PNAS_Directory.md",
    "Top_Academic_Journals_all.md",
    "Social Sciences Citation Index_20260715.md",
    "CSSCI_2025_2026.md",
    "Science Citation Index Expanded_20260715.md",
]
TOP5 = [
    "American Economic Review",
    "Econometrica",
    "Journal of Political Economy",
    "Quarterly Journal of Economics",
    "Review of Economic Studies",
]
CATALOG_VERSION = "2026-07-15"
CatalogIndex = dict[str, list[dict[str, Any]]]
# 不带前后 \s* 量词：两端的 \s* 与末尾锚点组合会产生二次方回溯。
# 调用方先 strip，再匹配后缀，行为等价且是线性的。
_DISPLAY_SUFFIX = re.compile(r"(?:\(网络首发\)|\[网络首发\]|【网络首发】|网络首发)$")
GENERIC_NCS_LABELS = (
    "五大",
    "部分",
    "子刊",
    "系列",
    "矩阵",
    "合作期刊",
)


def normalize_title(value: str) -> str:
    """Return a case- and punctuation-insensitive journal key."""
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("&", " and ")
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value)


def _normalize_conservative(value: str) -> str:
    """保留句点等可区分真实同形刊名的少量符号。"""
    value = unicodedata.normalize("NFKC", value).casefold().replace("&", " and ")
    value = re.sub(r"\s+", "", value)
    return re.sub(r"[^0-9a-z\u4e00-\u9fff.]+", "", value)


def _title_signatures(title: str) -> tuple[str, str]:
    normalized = normalize_title(title)
    conservative = _normalize_conservative(title)
    if normalized.startswith("the") and len(normalized) > 3:
        normalized = normalized[3:]
    if conservative.startswith("the") and len(conservative) > 3:
        conservative = conservative[3:]
    return normalized, conservative


def variant_key(title: str) -> str:
    """\u8fd4\u56de\u6bd4 normalize_title \u66f4\u4fdd\u5b88\u7684\u201c\u4e66\u5199\u53d8\u4f53\u952e\u201d\u3002

    normalize_title \u4f1a\u5265\u6389\u5168\u90e8\u6807\u70b9\u4e0e\u7a7a\u767d\uff0c\u56e0\u6b64\u4e24\u672c**\u771f\u6b63\u4e0d\u540c**\u7684\u671f\u520a
    \uff08\u5982 `A.B` \u4e0e `AB`\uff09\u4f1a\u843d\u8fdb\u540c\u4e00\u4e2a\u952e\uff0c\u5fc5\u987b\u4fdd\u7559\u4e3a ambiguous\u3002
    variant_key \u53ea\u5f52\u5e76\u540c\u4e00\u672c\u520a\u7684\u4e66\u5199\u5dee\u5f02\u2014\u2014\u51a0\u8bcd The \u6709\u65e0\u3001& \u4e0e and\u3001
    \u526f\u6807\u9898\u5206\u9694\u7b26 : / - / ,\u3001\u5168\u534a\u89d2\u62ec\u53f7\u4e0e\u5927\u5c0f\u5199\u2014\u2014\u4ece\u800c\u628a\u201c\u540c\u520a\u53d8\u4f53\u201d
    \u4e0e\u201c\u771f\u6b67\u4e49\u201d\u533a\u5206\u5f00\u3002
    """
    value = unicodedata.normalize("NFKC", title).casefold().replace("&", " and ")
    value = re.sub(r"[:\uff1a,\uff0c\-\u2013\u2014/()\uff08\uff09\[\]]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[4:] if value.startswith("the ") else value


def _read_catalog(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"综合期刊目录不存在：{CATALOG_FILENAME}")
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def _extract_source_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    pattern = re.compile(r"<!-- SOURCE_BEGIN: ([^>]+) -->")
    for match in pattern.finditer(text):
        filename = match.group(1).strip()
        if filename in blocks:
            raise ValueError(f"来源区块存在重复来源标记：{filename}")
        end_marker = f"<!-- SOURCE_END: {filename} -->"
        end = text.find(end_marker, match.end())
        if end < 0:
            raise ValueError(f"来源区块缺少结束标记：{filename}")
        blocks[filename] = text[match.end() : end].strip()
    return blocks


def validate_catalog(path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    """Validate the master catalog's priority and source-block structure."""
    text = _read_catalog(path)
    levels = [int(value) for value in re.findall(r"(?m)^  - level: (\d+)$", text)]
    groups = re.findall(r'(?m)^    group: "([^"]+)"$', text)
    blocks = _extract_source_blocks(text)
    version_match = re.search(r'(?m)^catalog_version: "([^"]+)"$', text)
    if levels != list(range(1, 11)):
        raise ValueError(f"综合目录检索层级无效：{levels}")
    if groups != EXPECTED_GROUPS:
        raise ValueError(f"综合目录优先级分组无效：{groups}")
    sources = list(blocks)
    if sources != EXPECTED_SOURCES:
        raise ValueError(f"综合目录来源文件无效：{sources}")
    if version_match is None or version_match.group(1) != CATALOG_VERSION:
        raise ValueError("综合目录版本无效")
    return {
        "valid": True,
        "catalog": str(path),
        "priority_levels": len(levels),
        "priority_groups": groups,
        "source_blocks": len(blocks),
        "sources": sources,
        "catalog_version": CATALOG_VERSION,
    }


def _clean_title(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^\d+\.\s+", "", raw)
    raw = re.sub(r"^\s*\*+\s*", "", raw)
    raw = raw.replace("**", "").strip()
    # 仅将 ASCII 空格连字符后的中文内容视作目录说明。英文并列刊名及其他
    # 连字符形式均保留，避免把实际刊名截断。
    if re.match(r"^[A-Za-z]", raw):
        raw = re.sub(r"\s*[（(][^（）()]+[）)](?=\s+-\s+)", "", raw)
        raw = re.sub(r"\s*[（(][^（）()]+[）)]\s*", "", raw)
        raw = re.sub(r"\s*[【[][^】\]]+[】\]](?=\s+-\s+)", "", raw)
        raw = re.sub(r"\s*[【[][^】\]]+[】\]]\s*", "", raw)
    dash = re.match(r"^(.+?) - ([一-鿿].*)$", raw)
    if dash:
        raw = dash.group(1).strip()
    return raw.strip(" .；;，,")


def _keys_for_title(title: str) -> set[str]:
    normalized, conservative = _title_signatures(title)
    keys = {normalized, conservative}
    # 某些目录记录将 Economic History 写作 Economics of History。此处按末词
    # 与词形构造保守的变体键，不依赖任何具体刊名。
    words = re.findall(r"[0-9a-z\u4e00-\u9fff]+", title.casefold())
    if len(words) >= 2 and words[-1] == "history":
        head = words[-2]
        keys.add(f"{head}ofhistory")
        if head.endswith("ic"):
            keys.add(f"{head[:-2]}icsofhistory")
    return {key for key in keys if key and len(key) >= 2}


def clean_lookup_title(value: str) -> tuple[str, str]:
    """Remove only the supported online-first display suffix."""
    normalized = unicodedata.normalize("NFKC", value).strip()
    cleaned = _DISPLAY_SUFFIX.sub("", normalized.rstrip()).strip()
    method = "controlled_display_suffix" if cleaned != normalized else "normalized_exact"
    return cleaned, method


def _add(
    index: CatalogIndex,
    title: str,
    level: int,
    group: str,
    source: str,
    *,
    ncs_internal_rank: int | None = None,
    subject_category: str | None = None,
) -> None:
    title = _clean_title(title)
    keys = _keys_for_title(title)
    if not keys or max(map(len, keys)) < 2:
        return

    # 用 variant_key 而非字符串精确相等判断“是否同一本刊”：同一本刊的不同
    # 书写形式（The 有无、& / and、副标题分隔符、全半角括号）会落进同一个
    # lookup key，若按精确相等去重则永远命中不到，会生成两个条目并被
    # lookup_journal 判为 ambiguous。
    normalized_signature, merge_signature = _title_signatures(title)
    existing = next(
        (
            candidate
            for key in keys
            for candidate in index.get(key, [])
            if candidate.get("normalized_signature") == normalized_signature
            and candidate.get("merge_signature") == merge_signature
        ),
        None,
    )
    if existing is None:
        existing = {
            "matched_title": title,
            "priority_level": level,
            "priority_group": group,
            "source_catalogs": [],
            "subject_categories": [],
            "ncs_internal_rank": ncs_internal_rank,
            "normalized_signature": normalized_signature,
            "merge_signature": merge_signature,
        }
    if source not in existing["source_catalogs"]:
        existing["source_catalogs"].append(source)
    if subject_category and subject_category not in existing["subject_categories"]:
        existing["subject_categories"].append(subject_category)
    if level < existing["priority_level"]:
        existing["matched_title"] = title
        existing["priority_level"] = level
        existing["priority_group"] = group
    if ncs_internal_rank is not None:
        old_rank = existing.get("ncs_internal_rank")
        existing["ncs_internal_rank"] = (
            ncs_internal_rank if old_rank is None else min(old_rank, ncs_internal_rank)
        )
    for key in keys:
        if existing not in index.setdefault(key, []):
            index[key].append(existing)


def _index_ncs(index: CatalogIndex, text: str) -> None:
    social_heading = "### 🌟 置顶板块：人文、哲学与社会科学（含交叉研究）期刊"
    first_main_heading = "### 第一部分：Nature"
    social_start = text.find(social_heading)
    social_end = text.find(first_main_heading)
    if social_start < 0 or social_end < 0 or social_start >= social_end:
        raise ValueError("NCS_PNAS 人文社科置顶板块结构无效")

    for line_match in re.finditer(r"(?m)^\s*\*\s+.*$", text):
        line = line_match.group(0)
        line_position = line_match.start()
        internal_rank = 1 if social_start < line_position < social_end else 2
        bold_titles = re.findall(r"\*\*([^*]+)\*\*", line)
        candidates = bold_titles or [re.sub(r"^\s*\*\s+", "", line)]
        for candidate in candidates:
            if any(label in candidate for label in GENERIC_NCS_LABELS):
                continue
            _add(
                index,
                candidate,
                2,
                "ncs_pnas",
                "NCS_PNAS_Directory.md",
                ncs_internal_rank=internal_rank,
            )


def _index_top(index: CatalogIndex, text: str) -> None:
    current_level = 7
    current_group = "other_top_journals"
    for line in text.splitlines():
        if "中文顶尖期刊目录" in line:
            current_level, current_group = 6, "chinese_top_journals"
        elif "英文综合顶尖期刊目录" in line:
            current_level, current_group = 7, "other_top_journals"
        elif "UTD24 期刊目录" in line:
            current_level, current_group = 3, "utd24"
        elif "FT50 期刊目录" in line:
            current_level, current_group = 4, "ft50"
        elif "细分领域顶尖期刊" in line or "Field Top Journals" in line:
            current_level, current_group = 5, "field_top"
        elif line.startswith("* "):
            _add(
                index,
                line,
                current_level,
                current_group,
                "Top_Academic_Journals_all.md",
            )


def _index_numbered_source(
    index: CatalogIndex,
    text: str,
    level: int,
    group: str,
    source: str,
) -> None:
    category: str | None = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(.+)$", line)
        if heading:
            category = heading.group(1).strip()
            continue
        match = re.match(r"^\d+\.\s+(.+)$", line)
        if match:
            _add(
                index,
                match.group(1),
                level,
                group,
                source,
                subject_category=category,
            )


def _index_cssci(index: CatalogIndex, text: str) -> None:
    for line in text.splitlines():
        match = re.match(r"^\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if match:
            _add(
                index,
                match.group(1),
                9,
                "cssci",
                "CSSCI_2025_2026.md",
                subject_category=match.group(2).strip(),
            )


def build_index(path: Path = DEFAULT_CATALOG) -> CatalogIndex:
    """Build a normalized journal index and retain each journal's best rank."""
    validate_catalog(path)
    text = _read_catalog(path)
    blocks = _extract_source_blocks(text)
    index: CatalogIndex = {}

    for title in TOP5:
        _add(
            index,
            title,
            1,
            "economics_top5",
            "Top_Academic_Journals_all.md",
            subject_category="经济学 Top 5",
        )

    _index_ncs(index, blocks["NCS_PNAS_Directory.md"])
    _index_top(index, blocks["Top_Academic_Journals_all.md"])
    _index_numbered_source(
        index,
        blocks["Social Sciences Citation Index_20260715.md"],
        8,
        "ssci",
        "Social Sciences Citation Index_20260715.md",
    )
    _index_cssci(index, blocks["CSSCI_2025_2026.md"])
    _index_numbered_source(
        index,
        blocks["Science Citation Index Expanded_20260715.md"],
        10,
        "scie",
        "Science Citation Index Expanded_20260715.md",
    )
    return index


def lookup_journal(index: CatalogIndex, journal: str) -> dict[str, Any]:
    """Look up one journal while preserving ambiguous normalized matches."""
    cleaned, method = clean_lookup_title(journal)
    candidates: list[dict[str, Any]] = []
    for key in _keys_for_title(cleaned):
        for candidate in index.get(key, []):
            if candidate not in candidates:
                candidates.append(candidate)
    query_signature = _title_signatures(cleaned)
    normalized_collisions = [
        candidate
        for candidate in candidates
        if candidate.get("normalized_signature") == query_signature[0]
    ]
    exact_candidates = [
        candidate
        for candidate in candidates
        if (
            candidate.get("normalized_signature"),
            candidate.get("merge_signature"),
        ) == query_signature
    ]
    if exact_candidates and len(normalized_collisions) <= len(exact_candidates):
        candidates = exact_candidates
    base = {
        "input": journal,
        "normalized": normalize_title(cleaned),
        "catalog_version": CATALOG_VERSION,
        "manual_review_required": True,
    }
    empty: dict[str, Any] = {
        "matched_title": None,
        "priority_level": None,
        "priority_group": None,
        "source_catalogs": [],
        "subject_categories": [],
        "ncs_internal_rank": None,
    }
    if not candidates:
        return base | {"status": "unmatched", "match_method": None, "candidates": [], **empty}
    signatures = {
        (candidate.get("normalized_signature"), candidate.get("merge_signature"))
        for candidate in candidates
    }
    if len(signatures) > 1:
        return base | {
            "status": "ambiguous",
            "match_method": None,
            "candidates": [item["matched_title"] for item in candidates],
            **empty,
        }
    return base | {
        "status": "matched",
        "match_method": method,
        "candidates": [],
        "manual_review_required": False,
        **candidates[0],
    }


def lookup_journals(path: Path, journals: list[str]) -> list[dict[str, Any]]:
    """Look up journals and return their highest priority memberships."""
    index = build_index(path)
    return [lookup_journal(index, journal) for journal in journals]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="校验综合期刊目录并查询期刊的最高检索层级。"
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="校验综合目录结构")
    lookup = subparsers.add_parser("lookup", help="查询一个或多个期刊")
    lookup.add_argument("journals", nargs="+")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        if args.command == "validate":
            result: Any = validate_catalog(args.catalog)
        else:
            result = lookup_journals(args.catalog, args.journals)
    except (FileNotFoundError, ValueError) as exc:
        # 面向普通用户的 CLI 不应抛裸 traceback
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
