"""WebVPN 专业检索的人工实机验证脚本，不进入发布包或 CI。"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cnki_search.professional_runtime import build_professional_runtime_from_env
from cnki_search.professional_service import SUPPORTED_GROUPS


FORBIDDEN_KEY_TOKENS = (
    "url",
    "cookie",
    "html",
    "storage_state",
    "profile",
)
SAMPLE_FIELDS = (
    "title",
    "journal_raw",
    "publication_year",
    "priority_level",
)


def _positive_limit(value: str) -> int:
    limit = int(value)
    if not 1 <= limit <= 50:
        raise argparse.ArgumentTypeError("limit 必须为 1 至 50")
    return limit


def _is_absolute_path(value: str) -> bool:
    return PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()


def _assert_sanitized(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).casefold()
            if any(token in normalized for token in FORBIDDEN_KEY_TOKENS):
                raise ValueError(f"输出包含敏感字段：{key}")
            _assert_sanitized(nested)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested in value:
            _assert_sanitized(nested)
        return
    if isinstance(value, Path) or (
        isinstance(value, str) and _is_absolute_path(value)
    ):
        raise ValueError("输出包含绝对路径")


def _summary(result: Mapping[str, Any], group: str) -> dict[str, Any]:
    records = result.get("records")
    if not isinstance(records, list):
        records = []
    sample = [
        {field: record.get(field) for field in SAMPLE_FIELDS}
        for record in records[:5]
        if isinstance(record, Mapping)
    ]
    return {
        "status": result.get("status"),
        "group": group,
        "record_count": len(records),
        "batches_completed": result.get("batches_completed", 0),
        "batches_total": result.get("batches_total", 0),
        "sample": sample,
    }


async def _run(args: argparse.Namespace) -> dict[str, Any]:
    runtime = await build_professional_runtime_from_env()
    try:
        result = await runtime.search_group(
            args.topic,
            args.group,
            limit=args.limit,
            year_from=args.year_from,
            year_to=args.year_to,
        )
    finally:
        await runtime.aclose()
    _assert_sanitized(result)
    summary = _summary(result, args.group)
    _assert_sanitized(summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="人工值守的 WebVPN 专业检索实机验证"
    )
    parser.add_argument("--topic", required=True)
    parser.add_argument("--group", choices=SUPPORTED_GROUPS, required=True)
    parser.add_argument("--limit", type=_positive_limit, default=5)
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    summary = asyncio.run(_run(build_parser().parse_args(argv)))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
