"""WebVPN 专业检索的人工实机验证脚本（环境版），不进入发布包或 CI。

失败时只输出固定的 {"status":"error","error":"webvpn_e2e_failed"}——这个
fail-closed 在安全上正确，但使「人工登录超时」与「真实缺陷」不可区分。
排查时应结合运行时状态目录 ~/.cnki-search-env（throttle 与 checkpoint.json）
判断执行到了哪一步，不要仅凭错误字符串下结论。
"""
from __future__ import annotations

import argparse
import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
import json
import math
import os
import sys
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cnki_search_env.professional_runtime import build_professional_runtime_from_env
from cnki_search_env.professional_service import SUPPORTED_GROUPS


FORBIDDEN_KEY_TOKENS = (
    "url",
    "cookie",
    "html",
    "storagestate",
    "token",
    "profile",
    "browser",
    "path",
    "session",
    "credential",
    "password",
)
SAFE_ERROR = {
    "status": "error",
    "error": "webvpn_e2e_failed",
}


class UnsafeOutputError(ValueError):
    pass


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, _message: str) -> None:
        raise UnsafeOutputError


def _positive_limit(value: str) -> int:
    limit = int(value)
    if not 1 <= limit <= 50:
        raise argparse.ArgumentTypeError("limit 必须为 1 至 50")
    return limit


def _is_absolute_path(value: str) -> bool:
    return PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()


def _reject_unsafe_output() -> None:
    raise UnsafeOutputError("E2E 输出不符合安全契约")


def _normalized_key(value: object) -> str:
    if type(value) is not str:
        _reject_unsafe_output()
    normalized = unicodedata.normalize("NFKC", value).casefold()
    if any(not character.isascii() for character in normalized):
        _reject_unsafe_output()
    if any(character.isdigit() for character in normalized):
        _reject_unsafe_output()
    return "".join(character for character in normalized if character.isalnum())


def _assert_sanitized(value: Any) -> None:
    if type(value) is dict:
        for key, nested in value.items():
            normalized = _normalized_key(key)
            if any(token in normalized for token in FORBIDDEN_KEY_TOKENS):
                _reject_unsafe_output()
            _assert_sanitized(nested)
        return
    if type(value) is list:
        for nested in value:
            _assert_sanitized(nested)
        return
    if type(value) is str:
        if _is_absolute_path(value):
            _reject_unsafe_output()
        return
    if type(value) is float:
        if not math.isfinite(value):
            _reject_unsafe_output()
        return
    if type(value) in {type(None), bool, int}:
        return
    _reject_unsafe_output()


def _required_value(
    mapping: dict[str, Any], key: str, expected_type: type,
) -> Any:
    if key not in mapping or type(mapping[key]) is not expected_type:
        _reject_unsafe_output()
    return mapping[key]


def _sample_record(record: object) -> dict[str, Any]:
    if type(record) is not dict:
        _reject_unsafe_output()
    sample = {
        "title": _required_value(record, "title", str),
        "journal_raw": _required_value(record, "journal_raw", str),
        "publication_year": _required_value(record, "publication_year", int),
        "priority_level": _required_value(record, "priority_level", int),
    }
    if "authors" in record:
        authors = record["authors"]
        if type(authors) is not list or any(type(author) is not str for author in authors):
            _reject_unsafe_output()
        sample["authors"] = list(authors)
    return sample


#: 发布前实机冒烟需要看到字段阶梯与分面证据，否则无法判断"结果为空"是
#: 真的没命中，还是分面根本没生效。允许值仍是闭集，不接受自由文本。
ALLOWED_TOPIC_FIELDS = ("TI", "SU", "KY", "TKA")
ALLOWED_SOURCE_CATEGORY_CODES = (None, "P0209", "P01")


def _controlled_topic_fields(mapping: dict[str, Any], key: str) -> list[str]:
    value = _required_value(mapping, key, list)
    for item in value:
        if type(item) is not str or item not in ALLOWED_TOPIC_FIELDS:
            _reject_unsafe_output()
    return list(value)


def _controlled_source_category_code(
    mapping: dict[str, Any], key: str,
) -> str | None:
    # 缺键与"本组无分面"必须可区分：服务漏发字段属契约破坏，不得静默当成 None。
    if key not in mapping:
        _reject_unsafe_output()
    value = mapping[key]
    if value is not None and (
        type(value) is not str or value not in ALLOWED_SOURCE_CATEGORY_CODES
    ):
        _reject_unsafe_output()
    return value


def _summary(result: object, group: str) -> dict[str, Any]:
    if type(result) is not dict:
        _reject_unsafe_output()
    status = _required_value(result, "status", str)
    batches_completed = _required_value(result, "batches_completed", int)
    batches_total = _required_value(result, "batches_total", int)
    records = _required_value(result, "records", list)
    sample = [_sample_record(record) for record in records[:5]]
    return {
        "status": status,
        "group": group,
        "record_count": len(records),
        "batches_completed": batches_completed,
        "batches_total": batches_total,
        "topic_fields_tried": _controlled_topic_fields(
            result, "topic_fields_tried"
        ),
        "source_category_code": _controlled_source_category_code(
            result, "source_category_code"
        ),
        "source_category_applied": _required_value(
            result, "source_category_applied", bool
        ),
        "eligible_record_count": _required_value(
            result, "eligible_record_count", int
        ),
        "first_page_only": _required_value(result, "first_page_only", bool),
        "complete": _required_value(result, "complete", bool),
        "human_intervention_required": _required_value(
            result, "human_intervention_required", bool
        ),
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
    parser = SafeArgumentParser(
        description="人工值守的 WebVPN 专业检索实机验证"
    )
    parser.add_argument("--topic", required=True)
    parser.add_argument("--group", choices=SUPPORTED_GROUPS, required=True)
    parser.add_argument("--limit", type=_positive_limit, default=5)
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    return parser


def _emit_safe_error() -> int:
    print(json.dumps(SAFE_ERROR, ensure_ascii=False), file=sys.stderr)
    return 1


@contextmanager
def _silence_process_output() -> Iterator[None]:
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    saved_stdout_fd: int | None = None
    saved_stderr_fd: int | None = None
    null_stdout = None
    null_stderr = None

    try:
        try:
            original_stdout.flush()
            original_stderr.flush()
            stdout_fd = original_stdout.fileno()
            stderr_fd = original_stderr.fileno()
            if (
                type(stdout_fd) is not int
                or stdout_fd < 0
                or type(stderr_fd) is not int
                or stderr_fd < 0
            ):
                _reject_unsafe_output()
        except BaseException:
            _reject_unsafe_output()

        saved_stdout_fd = os.dup(1)
        saved_stderr_fd = os.dup(2)
        null_stdout = open(os.devnull, "w", encoding="utf-8", newline="\n")
        null_stderr = open(os.devnull, "w", encoding="utf-8", newline="\n")
        os.dup2(null_stdout.fileno(), 1)
        os.dup2(null_stderr.fileno(), 2)
        sys.stdout = null_stdout
        sys.stderr = null_stderr
        yield
    finally:
        active_exception = sys.exc_info()[0] is not None
        cleanup_failed = False

        for stream in (sys.stdout, sys.stderr):
            try:
                stream.flush()
            except BaseException:
                cleanup_failed = True

        if saved_stdout_fd is not None:
            try:
                os.dup2(saved_stdout_fd, 1)
            except BaseException:
                cleanup_failed = True
        if saved_stderr_fd is not None:
            try:
                os.dup2(saved_stderr_fd, 2)
            except BaseException:
                cleanup_failed = True

        sys.stdout = original_stdout
        sys.stderr = original_stderr

        for stream in (null_stdout, null_stderr):
            if stream is not None:
                try:
                    stream.close()
                except BaseException:
                    cleanup_failed = True
        for descriptor in (saved_stdout_fd, saved_stderr_fd):
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except BaseException:
                    cleanup_failed = True

        if cleanup_failed and not active_exception:
            _reject_unsafe_output()


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return 0
        return _emit_safe_error()
    except BaseException:
        return _emit_safe_error()
    try:
        with _silence_process_output():
            summary = asyncio.run(_run(args))
        print(json.dumps(summary, ensure_ascii=False, allow_nan=False))
        return 0
    except BaseException:
        return _emit_safe_error()


if __name__ == "__main__":
    raise SystemExit(main())
