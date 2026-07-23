from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = (
    SKILL_ROOT / "references" / "Academic_Journal_Master_Directory_20260715.md"
)
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
_DISPLAY_SUFFIX = re.compile(r"\s*(?:\(网络首发\)|\[网络首发\]|【网络首发】|网络首发)\s*$")
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


def _read_catalog(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"综合期刊目录不存在：{path}")
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
    raw = re.split(r"\s+-\s+|：", raw, maxsplit=1)[0].strip()
    if re.match(r"^[A-Za-z]", raw):
        raw = re.sub(r"\s+[（(][^（）()]+[）)]$", "", raw)
    return raw.strip(" .；;，,")


def _keys_for_title(title: str) -> set[str]:
    key = normalize_title(title)
    keys = {key} if key else set()
    if key.startswith("the") and len(key) > 6:
        keys.add(key[3:])
    return keys


def clean_lookup_title(value: str) -> tuple[str, str]:
    """Remove only the supported online-first display suffix."""
    normalized = unicodedata.normalize("NFKC", value).strip()
    cleaned = _DISPLAY_SUFFIX.sub("", normalized).strip()
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

    existing = next(
        (
            candidate
            for key in keys
            for candidate in index.get(key, [])
            if candidate["matched_title"] == title
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
    if len(candidates) > 1:
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
    if args.command == "validate":
        result: Any = validate_catalog(args.catalog)
    else:
        result = lookup_journals(args.catalog, args.journals)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
