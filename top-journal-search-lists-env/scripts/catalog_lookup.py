from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


CATALOG_FILENAME = "environment_journal_catalog_v4.0.json"
SCHEMA_VERSION = "1.0"
CATALOG_VERSION = "4.0"
CATALOG_DATE = "2026-07-29"
REVISION_DATE = "2026-07-31"
EXPECTED_GROUPS = [
    "comprehensive_super_journals", "ncs_pnas_environment_flagships",
    "top_university_highest_consensus", "top_university_high_level",
    "environment_field_top", "chinese_environment_top", "other_formally_recognized",
    "environment_ssci", "environment_cssci", "environment_scie",
    "pku_core_natural_sciences", "pku_core_non_natural_sciences",
]
EXPECTED_LEVEL_COUNTS = [4, 17, 5, 45, 17, 6, 134, 324, 241, 1229, 1181, 561]
MIRRORED_REFERENCE_FILES = (
    "环境科学与工程学科顶尖期刊目录_v4.0.md",
    "environment_journal_catalog_v4.0.json",
    "environment_catalog_sources_v4.0.json",
    "environment_journal_match_audit_v4.0.md",
    "CSSCI_2025_2026.md",
    "北大中文核心期刊目录_2023_自然科学版.md",
    "北大中文核心期刊目录_2023_.md",
    "Social Sciences Citation Index_20260715.md",
    "Social Sciences Citation Index (SSCI).csv",
    "Science Citation Index Expanded_20260715.md",
    "Science Citation Index Expanded (SCIE).csv",
)


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


DEFAULT_CATALOG = _resolve_default_catalog()


def _exact_key(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def normalize_title(value: str) -> str:
    value = _exact_key(value).replace("&", " and ")
    value = re.sub(r"\s+", "", value)
    return re.sub(r"[.,:;·()\[\]{}'\"/\\-]+", "", value)


def _conservative_key(value: str) -> str:
    normalized = normalize_title(value)
    return normalized[3:] if normalized.startswith("the") and len(normalized) > 3 else normalized


@dataclass(frozen=True, slots=True)
class CatalogIndex:
    payload: dict[str, Any]
    by_journal_id: dict[str, dict[str, Any]]
    by_issn: dict[str, tuple[dict[str, Any], ...]]
    by_formal_title: dict[str, tuple[dict[str, Any], ...]]
    by_alias: dict[str, tuple[dict[str, Any], ...]]
    by_normalized_title: dict[str, tuple[dict[str, Any], ...]]
    records_by_priority_group: dict[str, tuple[dict[str, Any], ...]]
    records_by_cnki_scope: dict[str, tuple[dict[str, Any], ...]]


def _append(index: dict[str, list[dict[str, Any]]], key: str, record: dict[str, Any]) -> None:
    if key:
        index.setdefault(key, []).append(record)


def _freeze(index: dict[str, list[dict[str, Any]]]) -> dict[str, tuple[dict[str, Any], ...]]:
    return {key: tuple(value) for key, value in index.items()}


def _build_indexes(payload: dict[str, Any]) -> CatalogIndex:
    by_id: dict[str, dict[str, Any]] = {}
    issn: dict[str, list[dict[str, Any]]] = {}
    formal: dict[str, list[dict[str, Any]]] = {}
    aliases: dict[str, list[dict[str, Any]]] = {}
    normalized: dict[str, list[dict[str, Any]]] = {}
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in payload["journals"]:
        by_id[record["journal_id"]] = record
        _append(formal, _exact_key(record["formal_title"]), record)
        _append(normalized, _conservative_key(record["formal_title"]), record)
        for value in record.get("aliases", []):
            _append(aliases, _exact_key(value), record)
            _append(normalized, _conservative_key(value), record)
        for value in [*record.get("issn", []), *record.get("eissn", [])]:
            _append(issn, _exact_key(value), record)
        groups.setdefault(record["priority_group"], []).append(record)
    scopes: dict[str, tuple[dict[str, Any], ...]] = {}
    for scope_id, policy in payload["cnki_scopes"].items():
        scopes[scope_id] = tuple(by_id[item] for item in policy["eligible_journal_ids"])
    return CatalogIndex(
        payload=payload, by_journal_id=by_id, by_issn=_freeze(issn),
        by_formal_title=_freeze(formal), by_alias=_freeze(aliases),
        by_normalized_title=_freeze(normalized), records_by_priority_group=_freeze(groups),
        records_by_cnki_scope=scopes,
    )


def _validate_record_contract(record: Any) -> None:
    if not isinstance(record, dict):
        raise ValueError("环境目录记录必须为对象")
    required_types: dict[str, type[Any]] = {
        "journal_id": str,
        "formal_title": str,
        "formal_title_evidence_ids": list,
        "aliases": list,
        "issn": list,
        "eissn": list,
        "priority_group": str,
        "priority_decision": dict,
        "environment_subfields": list,
        "subject_categories": list,
        "formal_evidence": list,
        "evidence_ids": list,
        "index_memberships": list,
        "index_subject_categories": dict,
        "source_memberships": list,
        "source_catalogs": list,
        "catalog_version": str,
        "catalog_date": str,
        "revision_date": str,
        "manual_review_required": bool,
        "review_reasons": list,
        "cnki_routing": dict,
    }
    if not set(required_types) <= record.keys() or "priority_level" not in record or "ncs_internal_rank" not in record:
        raise ValueError("环境目录记录字段不完整")
    if any(not isinstance(record[name], expected) for name, expected in required_types.items()):
        raise ValueError("环境目录记录字段类型无效")
    if type(record["priority_level"]) is not int:
        raise ValueError("环境目录记录 priority_level 类型无效")
    if record["ncs_internal_rank"] is not None and type(record["ncs_internal_rank"]) is not int:
        raise ValueError("环境目录记录 ncs_internal_rank 类型无效")
    if (record["catalog_version"], record["catalog_date"], record["revision_date"]) != (CATALOG_VERSION, CATALOG_DATE, REVISION_DATE):
        raise ValueError("环境目录记录版本或日期无效")


def _validate_schema(payload: dict[str, Any]) -> None:
    required = {"schema_version", "catalog_version", "catalog_date", "revision_date", "priority_groups", "level_counts", "journals", "cnki_scopes", "data_sha256"}
    if not required <= payload.keys():
        raise ValueError("环境目录 JSON 字段不完整")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError("环境目录 JSON schema 版本无效")
    if not isinstance(payload["journals"], list) or not isinstance(payload["cnki_scopes"], dict):
        raise ValueError("环境目录 JSON 字段类型无效")
    for record in payload["journals"]:
        _validate_record_contract(record)


@lru_cache(maxsize=8)
def _load_catalog_cached(resolved_path: str, size: int, mtime_ns: int) -> CatalogIndex:
    del size, mtime_ns
    payload = json.loads(Path(resolved_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("环境目录 JSON 根对象无效")
    _validate_schema(payload)
    return _build_indexes(payload)


def load_catalog(path: Path = DEFAULT_CATALOG) -> CatalogIndex:
    resolved = Path(path).resolve()
    stat = resolved.stat()
    return _load_catalog_cached(str(resolved), stat.st_size, stat.st_mtime_ns)


def _canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("环境目录不得包含浮点数")
    if isinstance(value, dict):
        for item in value.values():
            _assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_float(item)


def _validate_json(index: CatalogIndex, path: Path) -> dict[str, Any]:
    payload = index.payload
    _validate_schema(payload)
    if (payload["catalog_version"], payload["catalog_date"], payload["revision_date"]) != (CATALOG_VERSION, CATALOG_DATE, REVISION_DATE):
        raise ValueError("环境目录版本或日期无效")
    if payload["priority_groups"] != EXPECTED_GROUPS or payload["level_counts"] != EXPECTED_LEVEL_COUNTS:
        raise ValueError("环境目录层级定义无效")
    records = payload["journals"]
    if not isinstance(records, list) or len(records) != sum(EXPECTED_LEVEL_COUNTS):
        raise ValueError("环境目录期刊数量无效")
    _assert_no_float(payload)
    ids = [record.get("journal_id") for record in records]
    titles = [record.get("formal_title") for record in records]
    if len(set(ids)) != len(records) or len(set(titles)) != len(records):
        raise ValueError("环境目录存在重复期刊标识或刊名")
    signature = [(record.get("journal_id"), record.get("priority_level"), record.get("priority_group"), record.get("ncs_internal_rank")) for record in records]
    if len(set(signature)) != len(records):
        raise ValueError("环境目录存在跨层级重复")
    counts = [sum(record.get("priority_level") == level for record in records) for level in range(1, 13)]
    if counts != EXPECTED_LEVEL_COUNTS:
        raise ValueError("环境目录各层级数量无效")
    if any(record.get("priority_group") != EXPECTED_GROUPS[record.get("priority_level", 0) - 1] for record in records):
        raise ValueError("环境目录层级与分组不一致")
    draft = dict(payload)
    draft["data_sha256"] = "{{DATA_SHA256}}"
    if hashlib.sha256(_canonical_json_bytes(draft)).hexdigest() != payload["data_sha256"]:
        raise ValueError("环境目录数据 SHA-256 无效")
    return {"valid": True, "catalog": str(path.resolve()), "catalog_version": CATALOG_VERSION, "catalog_date": CATALOG_DATE, "revision_date": REVISION_DATE, "priority_levels": 12, "priority_groups": EXPECTED_GROUPS, "level_counts": counts, "unique_journals": len(records)}


def _default_companions(path: Path) -> tuple[Path, Path, Path]:
    references = path.parent
    return (
        references / "环境科学与工程学科顶尖期刊目录_v4.0.md",
        references / "environment_catalog_sources_v4.0.json",
        references / "environment_journal_match_audit_v4.0.md",
    )


def _peer_references(path: Path) -> Path:
    references = path.parent
    if references.parent.name == "src":
        return references.parent.parent.parent / "references"
    return references.parent / "mcpb" / "src" / "references"


def _validate_companions(markdown: Path, sources: Path, audit_summary: Path) -> list[str]:
    for item in (markdown, sources, audit_summary):
        if not item.is_file():
            raise ValueError(f"环境目录伴随文件不存在：{item.name}")
    if "v4.0" not in markdown.read_text(encoding="utf-8"):
        raise ValueError("环境目录 Markdown 版本无效")
    source_payload = json.loads(sources.read_text(encoding="utf-8"))
    artifacts = source_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 7:
        raise ValueError("环境目录来源清单版本无效")
    if "v4.0" not in audit_summary.read_text(encoding="utf-8"):
        raise ValueError("环境目录审计摘要版本无效")
    return [item.name for item in (markdown, sources, audit_summary)]


def _validate_mirror(references: Path, mirror: Path) -> int:
    if not mirror.is_dir():
        raise ValueError("环境目录镜像 references 不存在")
    for name in MIRRORED_REFERENCE_FILES:
        left, right = references / name, mirror / name
        if not left.is_file() or not right.is_file() or left.read_bytes() != right.read_bytes():
            raise ValueError(f"环境目录镜像不一致：{name}")
    return len(MIRRORED_REFERENCE_FILES)


def validate_catalog(path: Path = DEFAULT_CATALOG, *, markdown: Path | None = None, sources: Path | None = None, audit_summary: Path | None = None, mirror_references: Path | None = None) -> dict[str, Any]:
    resolved = Path(path).resolve()
    result = _validate_json(load_catalog(resolved), resolved)
    is_default = resolved == DEFAULT_CATALOG.resolve()
    companion_args = (markdown, sources, audit_summary)
    if (any(item is not None for item in companion_args) or mirror_references is not None) and not all(item is not None for item in companion_args):
        raise ValueError("必须提供完整的三件环境目录伴随文件")
    if is_default:
        markdown, sources, audit_summary = _default_companions(resolved)
    if markdown is None:
        result |= {"validation_scope": "json_only", "companion_files_verified": [], "mirrored_files_verified": 0}
        return result
    assert sources is not None and audit_summary is not None
    result["companion_files_verified"] = _validate_companions(markdown, sources, audit_summary)
    mirror = mirror_references if mirror_references is not None else _peer_references(resolved)
    result |= {"validation_scope": "full", "mirrored_files_verified": _validate_mirror(resolved.parent, mirror)}
    return result


def _empty_result(journal: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "input": journal, "normalized": normalize_title(journal), "status": "unmatched", "match_method": None, "candidates": [],
        "journal_id": None, "matched_title": None, "priority_level": None, "priority_group": None, "environment_subfields": [], "subject_categories": [], "formal_evidence": [], "index_memberships": [], "source_catalogs": [], "ncs_internal_rank": None, "aliases": [], "index_subject_categories": {}, "source_memberships": [], "revision_date": payload["revision_date"], "catalog_version": payload["catalog_version"], "catalog_date": payload["catalog_date"], "manual_review_required": True,
    }


def lookup_journal(index: CatalogIndex, journal: str) -> dict[str, Any]:
    exact = _exact_key(journal)
    candidates = index.by_formal_title.get(exact, ())
    method = "formal_title_exact"
    if not candidates:
        candidates, method = index.by_alias.get(exact, ()), "controlled_alias"
    if not candidates:
        candidates, method = index.by_normalized_title.get(_conservative_key(journal), ()), "conservative_normalized"
    result = _empty_result(journal, index.payload)
    unique = {record["journal_id"]: record for record in candidates}
    if not unique:
        return result
    if len(unique) > 1:
        return result | {"status": "ambiguous", "candidates": sorted(record["formal_title"] for record in unique.values())}
    record = next(iter(unique.values()))
    matched = json.loads(json.dumps(record, ensure_ascii=False))
    matched["matched_title"] = matched.pop("formal_title")
    return result | matched | {"status": "matched", "match_method": method, "candidates": [], "manual_review_required": False}


def lookup_journals(path: Path, journals: list[str]) -> list[dict[str, Any]]:
    index = load_catalog(path)
    return [lookup_journal(index, journal) for journal in journals]


def journals_by_group(group: str, path: Path = DEFAULT_CATALOG) -> list[str]:
    try:
        records = load_catalog(path).records_by_priority_group[group]
    except KeyError as exc:
        raise ValueError(f"目录中没有 priority_group='{group}' 的期刊") from exc
    return sorted(record["formal_title"] for record in records)


def cnki_scope(scope_id: str, path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    index = load_catalog(path)
    try:
        policy = dict(index.payload["cnki_scopes"][scope_id])
        records = index.records_by_cnki_scope[scope_id]
    except KeyError as exc:
        raise ValueError(f"未知 CNKI scope：{scope_id}") from exc
    policy["catalog_version"] = index.payload["catalog_version"]
    policy["journal_titles"] = [record["formal_title"] for record in records]
    return policy


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="校验环境期刊目录并查询最高检索层级。")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--audit-summary", type=Path)
    parser.add_argument("--mirror-references", type=Path)
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
        if args.command == "validate":
            result: Any = validate_catalog(args.catalog, markdown=args.markdown, sources=args.sources, audit_summary=args.audit_summary, mirror_references=args.mirror_references)
        else:
            result = lookup_journals(args.catalog, args.journals)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
