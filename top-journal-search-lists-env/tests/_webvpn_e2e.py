"""人工值守 WebVPN 验收 CLI；显式运行才会启动浏览器并提交检索。

需要本人通过机构授权完成登录与验证码，不可用于定时任务，不得自动破解。
只输出经过闭集校验的题录摘要；不保存票据、页面或原始诊断。
运行时的 Python、原生和子进程输出均丢弃，人工操作在可见浏览器内完成。
文件描述符重定向是进程级操作，请将本脚本作为独立 CLI 使用。
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import ctypes
import json
import math
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, Iterator


class UnsafeOutputError(ValueError):
    """输出不符合受控契约；异常不携带输入值。"""


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


async def build_professional_runtime_from_env() -> Any:
    # 延迟导入，使导入阶段的诊断和依赖错误也处于输出隔离范围内。
    from cnki_search_env.professional_runtime import build_professional_runtime_from_env as build

    return await build()


_SENSITIVE_KEYS = (
    "cookie", "token", "session", "profile", "password", "credential",
    "storage", "browser", "context", "url", "path", "home", "html",
)
_ADDRESS = re.compile(
    r"(?i)(?:[a-z][a-z0-9+.-]*://|www\.|[a-z]:[\\/]|\\\\|"
    r"(?:^|\s)[/~][\w.]|[\w.+-]+@[\w.-]+\.[a-z]{2,}|"
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\b[\w-]+\.(?:com|org|net|edu|cn)\b)"
)
_STATUSES = frozenset((
    "success", "no_results", "partial", "rate_limited", "challenge_detected",
    "login_required", "forbidden", "page_contract_changed", "configuration_error",
    "network_error", "no_data_retry_later",
))


def _assert_json_tree(value: Any) -> None:
    """不接受任意对象或混淆字段名，未知但规范的非敏感字段仅丢弃。"""
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str or re.fullmatch(r"[A-Za-z_]+", key) is None:
                raise UnsafeOutputError()
            # 目录索引可使用 PKU_CORE 等大写键；敏感键检查仍不区分大小写。
            if any(token in key.casefold() for token in _SENSITIVE_KEYS):
                raise UnsafeOutputError()
            _assert_json_tree(child)
    elif type(value) is list:
        for child in value:
            _assert_json_tree(child)
    elif value is None or type(value) in (str, int, bool):
        return
    elif type(value) is float and math.isfinite(value):
        return
    else:
        raise UnsafeOutputError()


def _text(value: Any, maximum: int) -> str:
    if type(value) is not str or not value.strip() or len(value) > maximum:
        raise UnsafeOutputError()
    normalized = unicodedata.normalize("NFKC", value)
    if _ADDRESS.search(normalized) or any(
        unicodedata.category(character) in {"Cc", "Cf"} for character in value
    ):
        raise UnsafeOutputError()
    if re.search(r"(?i)(?:cookie|token|password|credential|authorization)\s*[:=]", normalized):
        raise UnsafeOutputError()
    return value


def _count(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise UnsafeOutputError()
    return value


def _summary(result: Any, group: str) -> dict[str, Any]:
    _assert_json_tree(result)
    if type(result) is not dict:
        raise UnsafeOutputError()
    required = {
        "status", "records", "batches_completed", "batches_total",
        "topic_fields_tried", "source_category_code", "source_category_applied",
        "eligible_record_count", "first_page_only", "complete",
        "human_intervention_required",
    }
    if not required <= result.keys():
        raise UnsafeOutputError()
    status = result["status"]
    if type(status) is not str or status not in _STATUSES:
        raise UnsafeOutputError()
    fields = result["topic_fields_tried"]
    if type(fields) is not list or any(
        type(field) is not str or field not in {"TI", "SU", "KY", "TKA"}
        for field in fields
    ):
        raise UnsafeOutputError()
    category = result["source_category_code"]
    if category is not None and (type(category) is not str or category not in {"P0209", "P01"}):
        raise UnsafeOutputError()
    boolean_keys = (
        "source_category_applied", "first_page_only", "complete", "human_intervention_required",
    )
    if any(type(result[key]) is not bool for key in boolean_keys):
        raise UnsafeOutputError()
    records = result["records"]
    if type(records) is not list:
        raise UnsafeOutputError()
    sample = []
    for record in records:
        if type(record) is not dict:
            raise UnsafeOutputError()
        year = record.get("publication_year")
        priority = record.get("priority_level")
        if type(year) is not int or not 1900 <= year <= date.today().year + 1:
            raise UnsafeOutputError()
        if priority is not None and (type(priority) is not int or not 1 <= priority <= 12):
            raise UnsafeOutputError()
        item = {
            "title": _text(record.get("title"), 500),
            "journal_raw": _text(record.get("journal_raw"), 300),
            "publication_year": year,
            "priority_level": priority,
        }
        if "authors" in record:
            authors = record["authors"]
            if type(authors) is not list or len(authors) > 50:
                raise UnsafeOutputError()
            item["authors"] = [_text(author, 120) for author in authors]
        if len(sample) < 3:
            sample.append(item)
    summary = {
        "status": status,
        "group": _text(group, 80),
        "record_count": len(records),
        "batches_completed": _count(result["batches_completed"]),
        "batches_total": _count(result["batches_total"]),
        "topic_fields_tried": list(fields),
        "source_category_code": category,
        "source_category_applied": result["source_category_applied"],
        "eligible_record_count": _count(result["eligible_record_count"]),
        "first_page_only": result["first_page_only"],
        "complete": result["complete"],
        "human_intervention_required": result["human_intervention_required"],
        "sample": sample,
    }
    if summary["batches_completed"] > summary["batches_total"]:
        raise UnsafeOutputError()
    return summary


@contextlib.contextmanager
def _isolated_output() -> Iterator[None]:
    """先备份所有描述符，再重定向；部分安装失败也必须恢复原状。"""
    stdout, stderr = sys.stdout, sys.stderr
    streams = [stdout, stderr]
    for original in (sys.__stdout__, sys.__stderr__):
        if original is not None and all(original is not stream for stream in streams):
            streams.append(original)
    stdout.flush()
    stderr.flush()
    # C stdio 及运行时预先保存的 Python 流可能延迟到 FD 恢复后才写出。
    # 在隔离仍生效时排空这些缓冲区，避免原生扩展诊断逃逸。
    native_flush = ctypes.CDLL("ucrtbase.dll" if os.name == "nt" else None).fflush
    native_flush.argtypes = [ctypes.c_void_p]
    native_flush.restype = ctypes.c_int
    descriptors = sorted({1, 2, stdout.fileno(), stderr.fileno()})
    saved: list[tuple[int, int]] = []
    redirected: list[tuple[int, int]] = []
    with open(os.devnull, "w", encoding="utf-8") as sink:
        try:
            for descriptor in descriptors:
                saved.append((descriptor, os.dup(descriptor)))
            for descriptor, backup in saved:
                os.dup2(sink.fileno(), descriptor)
                redirected.append((descriptor, backup))
            sys.stdout = sys.stderr = sink
            yield
        finally:
            try:
                sink.flush()
                for stream in streams:
                    stream.flush()
                if native_flush(None) != 0:
                    raise UnsafeOutputError()
            finally:
                sys.stdout, sys.stderr = stdout, stderr
                try:
                    for descriptor, backup in reversed(redirected):
                        os.dup2(backup, descriptor)
                finally:
                    for _descriptor, backup in saved:
                        os.close(backup)


def _controlled_reason(error: BaseException) -> str | None:
    from cnki_search_env.browser import BrowserUnavailableError
    from cnki_search_env.webvpn import WebVpnLoginTimeout, WebVpnNavigationError, WebVpnWindowClosed

    for error_type, reason in (
        (BrowserUnavailableError, "browser_unavailable"),
        (WebVpnLoginTimeout, "login_timeout"),
        (WebVpnWindowClosed, "browser_window_closed"),
        (WebVpnNavigationError, "page_contract_changed"),
    ):
        if isinstance(error, error_type):
            return reason
    return None


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UnsafeOutputError()


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = _Parser(prog="webvpn-e2e", description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--group", required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    args = parser.parse_args(argv)
    if not args.topic.strip() or not 1 <= args.limit <= 50:
        raise UnsafeOutputError()
    years = [year for year in (args.year_from, args.year_to) if year is not None]
    if any(not 1900 <= year <= date.today().year + 1 for year in years):
        raise UnsafeOutputError()
    if len(years) == 2 and args.year_from > args.year_to:
        raise UnsafeOutputError()
    return args


async def _run(args: argparse.Namespace) -> dict[str, Any]:
    from cnki_search_env.professional_service import SUPPORTED_GROUPS

    if args.group not in SUPPORTED_GROUPS:
        raise UnsafeOutputError()
    runtime = await build_professional_runtime_from_env()
    try:
        result = await runtime.search_group(
            args.topic, args.group, limit=args.limit,
            year_from=args.year_from, year_to=args.year_to,
        )
        return _summary(result, args.group)
    finally:
        await runtime.aclose()


def main(argv: list[str] | None = None) -> int:
    failure = {"status": "error", "error": "webvpn_e2e_failed"}
    summary = None
    try:
        args = _arguments(argv)
        with _isolated_output():
            try:
                summary = asyncio.run(_run(args))
            except BaseException as error:
                reason = _controlled_reason(error)
                if reason is not None:
                    failure["reason"] = reason
    except SystemExit as error:
        if error.code == 0:
            return 0
    except BaseException:
        summary = None
    if summary is None:
        print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, allow_nan=False))
    return int(
        summary["status"] not in {"success", "no_results"}
        or not summary["complete"] or summary["human_intervention_required"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
