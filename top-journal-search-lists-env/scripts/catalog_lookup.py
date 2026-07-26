from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


CATALOG_FILENAME = "环境科学与工程学科顶尖期刊目录_v3.0.md"
CATALOG_VERSION = "3.0"
CATALOG_DATE = "2026-07-26"
CATALOG_SOURCE = CATALOG_FILENAME
INDEX_SOURCE_CATALOGS = {
    "SSCI": "Social Sciences Citation Index_20260715.md",
    "CSSCI": "CSSCI_2025_2026.md",
    "SCIE": "Science Citation Index Expanded_20260715.md",
}
EXPECTED_GROUPS = [
    "comprehensive_super_journals",
    "ncs_pnas_environment_flagships",
    "top_university_highest_consensus",
    "top_university_high_level",
    "environment_field_top",
    "chinese_environment_top",
    "other_formally_recognized",
    "environment_ssci",
    "environment_cssci",
    "environment_scie",
]
EXPECTED_LEVEL_NAMES = [
    "综合超一流主刊",
    "NCS、PNAS及环境旗舰子刊",
    "国内顶尖高校最高等级共识期刊",
    "国内顶尖高校高等级期刊",
    "广义环境学科各细分领域顶尖期刊",
    "中文顶尖期刊",
    "其他获得正式认可的高水平期刊",
    "环境相关SSCI期刊",
    "环境相关CSSCI期刊",
    "环境相关SCIE期刊",
]
EXPECTED_LEVEL_COUNTS = [4, 17, 5, 45, 17, 6, 134, 324, 241, 1229]
EXPECTED_UNIQUE_JOURNALS = 2022
MAIN_START = "## 四、十级主目录"
MAIN_END = "## 附录一：环境相关SCIE分类目录"
CatalogIndex = dict[str, list[dict[str, Any]]]
_DISPLAY_SUFFIX = re.compile(r"(?:\(网络首发\)|\[网络首发\]|【网络首发】|网络首发)$")
_LEVEL_HEADING = re.compile(r"^### 第([一二三四五六七八九十]+)级：(.+)$")
_CHINESE_LEVELS = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def _resolve_default_catalog() -> Path:
    configured = os.environ.get("CNKI_ENV_CATALOG_PATH")
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


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("&", " and ")
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value)


def _normalize_conservative(value: str) -> str:
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
    value = unicodedata.normalize("NFKC", title).casefold().replace("&", " and ")
    value = re.sub(r"[:：,，\-\u2013\u2014/()（）\[\]]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[4:] if value.startswith("the ") else value


def _keys_for_title(title: str) -> set[str]:
    return {key for key in _title_signatures(title) if key and len(key) >= 2}


def clean_lookup_title(value: str) -> tuple[str, str]:
    normalized = unicodedata.normalize("NFKC", value).strip()
    cleaned = _DISPLAY_SUFFIX.sub("", normalized.rstrip()).strip()
    method = "controlled_display_suffix" if cleaned != normalized else "normalized_exact"
    return cleaned, method


def _read_catalog(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"环境期刊目录不存在：{CATALOG_FILENAME}")
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def _main_text(text: str) -> str:
    start = text.find(MAIN_START)
    end = text.find(MAIN_END)
    if start < 0 or end < 0 or start >= end:
        raise ValueError("环境目录十级主目录边界无效")
    return text[start:end]


def _split_values(value: str) -> list[str]:
    if not value or value.strip() in {"—", "-"}:
        return []
    values = re.split(r"<br\s*/?>", value, flags=re.IGNORECASE)
    return [re.sub(r"\*\*", "", item).strip() for item in values if item.strip() not in {"", "—", "-"}]


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _clean_title(raw: str) -> tuple[str, int | None]:
    parts = _split_values(raw)
    if not parts:
        return "", None
    rank: int | None = None
    for part in parts[1:]:
        match = re.fullmatch(r"内部顺序[：:]\s*([123])", part)
        if match:
            rank = int(match.group(1))
    title = re.sub(r"\*\*", "", parts[0]).strip(" .；;，,")
    return title, rank


def _parse_records(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    main = _main_text(text)
    records: list[dict[str, Any]] = []
    level_names: list[str] = []
    level: int | None = None
    headers: list[str] | None = None
    for line in main.splitlines():
        heading = _LEVEL_HEADING.match(line)
        if heading:
            level = _CHINESE_LEVELS.get(heading.group(1))
            if level is None:
                raise ValueError(f"无法识别环境目录层级：{heading.group(1)}")
            level_names.append(heading.group(2).strip())
            headers = None
            continue
        if level is None or not line.startswith("|"):
            continue
        cells = _split_row(line)
        if "期刊名称" in cells and "序号" in cells:
            headers = cells
            continue
        if headers is None or not cells or not re.fullmatch(r"\d+", cells[0]):
            continue
        if len(cells) != len(headers):
            raise ValueError(f"第{level}级表格列数不一致：{line[:80]}")
        row = dict(zip(headers, cells, strict=True))
        title, ncs_rank = _clean_title(row["期刊名称"])
        if not title:
            raise ValueError(f"第{level}级存在空期刊名称")
        environment_subfields = _split_values(row.get("环境细分领域", ""))
        formal_evidence = _split_values(row.get("正式证据", ""))
        if level <= 7:
            index_memberships = _split_values(row.get("数据库及来源类别", ""))
            source_catalogs = [CATALOG_SOURCE]
        else:
            index_memberships = _split_values(row.get("原始学科类别", ""))
            source_catalogs = [
                INDEX_SOURCE_CATALOGS.get(value, value)
                for value in _split_values(row.get("收录来源", ""))
            ]
        records.append(
            {
                "matched_title": title,
                "priority_level": level,
                "priority_group": EXPECTED_GROUPS[level - 1],
                "environment_subfields": environment_subfields,
                "subject_categories": list(environment_subfields),
                "formal_evidence": formal_evidence,
                "index_memberships": index_memberships,
                "source_catalogs": source_catalogs,
                "ncs_internal_rank": ncs_rank,
                "catalog_version": CATALOG_VERSION,
                "catalog_date": CATALOG_DATE,
            }
        )
    return records, level_names


def _content_hash_is_valid(text: str) -> bool:
    match = re.search(r"\| 内容SHA-256 \| `([0-9a-fA-F]{64})` \|", text)
    if match is None:
        return False
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    placeholder = normalized[: match.start(1)] + "{{SHA256}}" + normalized[match.end(1) :]
    return hashlib.sha256(placeholder.encode("utf-8")).hexdigest() == match.group(1).casefold()


def _add(
    index: CatalogIndex,
    title: str,
    level: int,
    group: str,
    *,
    environment_subfields: list[str],
    formal_evidence: list[str],
    index_memberships: list[str],
    source_catalogs: list[str],
    ncs_internal_rank: int | None = None,
) -> None:
    title = title.strip()
    keys = _keys_for_title(title)
    if not keys:
        return
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
            "environment_subfields": [],
            "subject_categories": [],
            "formal_evidence": [],
            "index_memberships": [],
            "source_catalogs": [],
            "ncs_internal_rank": ncs_internal_rank,
            "catalog_version": CATALOG_VERSION,
            "catalog_date": CATALOG_DATE,
            "normalized_signature": normalized_signature,
            "merge_signature": merge_signature,
        }
    for field, values in (
        ("environment_subfields", environment_subfields),
        ("subject_categories", environment_subfields),
        ("formal_evidence", formal_evidence),
        ("index_memberships", index_memberships),
        ("source_catalogs", source_catalogs),
    ):
        for value in values:
            if value not in existing[field]:
                existing[field].append(value)
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


def _build_index_from_records(records: list[dict[str, Any]]) -> CatalogIndex:
    index: CatalogIndex = {}
    for record in records:
        _add(
            index,
            title=record["matched_title"],
            level=record["priority_level"],
            group=record["priority_group"],
            environment_subfields=record["environment_subfields"],
            formal_evidence=record["formal_evidence"],
            index_memberships=record["index_memberships"],
            source_catalogs=record["source_catalogs"],
            ncs_internal_rank=record["ncs_internal_rank"],
        )
    return index


def _unique_index_records(index: CatalogIndex) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[int] = set()
    for candidates in index.values():
        for candidate in candidates:
            marker = id(candidate)
            if marker not in seen:
                seen.add(marker)
                records.append(candidate)
    return records


def validate_catalog(path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    text = _read_catalog(path)
    if not _content_hash_is_valid(text):
        raise ValueError("环境目录内容SHA-256无效")
    version = re.search(r'(?m)^version: "([^"]+)"$', text)
    date = re.search(r'(?m)^catalog_date: "([^"]+)"$', text)
    records, level_names = _parse_records(text)
    if version is None or version.group(1) != CATALOG_VERSION:
        raise ValueError("环境目录版本无效")
    if date is None or date.group(1) != CATALOG_DATE:
        raise ValueError("环境目录日期无效")
    if level_names != EXPECTED_LEVEL_NAMES:
        raise ValueError(f"环境目录层级名称无效：{level_names}")
    counts = [
        sum(record["priority_level"] == level for record in records)
        for level in range(1, 11)
    ]
    if counts != EXPECTED_LEVEL_COUNTS:
        raise ValueError(f"环境目录各级数量无效：{counts}")
    titles = [record["matched_title"] for record in records]
    if len(set(titles)) != EXPECTED_UNIQUE_JOURNALS:
        raise ValueError(f"环境目录唯一期刊数无效：{len(set(titles))}")
    index = _build_index_from_records(records)
    collisions = {
        key: [candidate["matched_title"] for candidate in candidates]
        for key, candidates in index.items()
        if len(
            {
                (
                    candidate["normalized_signature"],
                    candidate["merge_signature"],
                )
                for candidate in candidates
            }
        )
        > 1
    }
    if collisions:
        sample = dict(list(collisions.items())[:5])
        raise ValueError(f"环境目录存在未解释的规范化冲突：{sample}")
    if len(_unique_index_records(index)) != EXPECTED_UNIQUE_JOURNALS:
        raise ValueError("环境目录存在跨层级重复或未解释的书写变体")
    return {
        "valid": True,
        "catalog": str(path.resolve()),
        "catalog_version": CATALOG_VERSION,
        "catalog_date": CATALOG_DATE,
        "priority_levels": 10,
        "priority_groups": EXPECTED_GROUPS,
        "level_counts": counts,
        "unique_journals": EXPECTED_UNIQUE_JOURNALS,
    }


def build_index(path: Path = DEFAULT_CATALOG) -> CatalogIndex:
    validate_catalog(path)
    records, _level_names = _parse_records(_read_catalog(path))
    return _build_index_from_records(records)


def lookup_journal(index: CatalogIndex, journal: str) -> dict[str, Any]:
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
        )
        == query_signature
    ]
    if exact_candidates and len(normalized_collisions) <= len(exact_candidates):
        candidates = exact_candidates
    base = {
        "input": journal,
        "normalized": normalize_title(cleaned),
        "catalog_version": CATALOG_VERSION,
        "catalog_date": CATALOG_DATE,
        "manual_review_required": True,
    }
    empty: dict[str, Any] = {
        "matched_title": None,
        "priority_level": None,
        "priority_group": None,
        "environment_subfields": [],
        "subject_categories": [],
        "formal_evidence": [],
        "index_memberships": [],
        "source_catalogs": [],
        "ncs_internal_rank": None,
    }
    if not candidates:
        return base | {"status": "unmatched", "match_method": None, "candidates": [], **empty}
    signatures = {
        (candidate["normalized_signature"], candidate["merge_signature"])
        for candidate in candidates
    }
    if len(signatures) > 1:
        return base | {
            "status": "ambiguous",
            "match_method": None,
            "candidates": sorted(candidate["matched_title"] for candidate in candidates),
            **empty,
        }
    matched = {
        key: value
        for key, value in candidates[0].items()
        if key not in {"normalized_signature", "merge_signature"}
    }
    return base | {
        "status": "matched",
        "match_method": method,
        "candidates": [],
        "manual_review_required": False,
        **matched,
    }


def lookup_journals(path: Path, journals: list[str]) -> list[dict[str, Any]]:
    index = build_index(path)
    return [lookup_journal(index, journal) for journal in journals]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="校验环境期刊目录并查询最高检索层级。")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="校验环境目录结构")
    lookup = subparsers.add_parser("lookup", help="批量查询期刊")
    lookup.add_argument("journals", nargs="+")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        result: Any
        if args.command == "validate":
            result = validate_catalog(args.catalog)
        else:
            result = lookup_journals(args.catalog, args.journals)
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
