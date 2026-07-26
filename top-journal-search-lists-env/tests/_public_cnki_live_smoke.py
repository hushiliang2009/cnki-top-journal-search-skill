from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cnki_search_env.models import SearchRequest, SearchStatus
from cnki_search_env.service import CnkiPublicSearchService
from cnki_search_env.session import PublicCnkiSession


FORBIDDEN_FIELD_TOKENS = ("url", "cookie", "token", "session")
ACCEPTED_STATUSES = {SearchStatus.SUCCESS, SearchStatus.PARTIAL}
EXPECTED_RESULT_DOMAIN = "kns.cnki.net"


class ObservedPublicCnkiSession:
    """包装运行时会话，仅在进程内保留最终页面域名，避免把 URL 写入验证证据。

    会话协议必须与 service.py 一致（异步上下文管理器 + 异步 search）。运行时
    从同步迁到异步后，本脚本曾因仍调用 __enter__ 而整体失效；离线注入测试
    test_live_smoke_speaks_the_current_async_session_protocol 现锁定该协议。
    """

    def __init__(self, inner_factory: Callable[[], Any], observer: dict[str, Any]) -> None:
        self._inner = inner_factory()
        self._observer = observer

    async def __aenter__(self) -> "ObservedPublicCnkiSession":
        await self._inner.__aenter__()
        return self

    async def search(self, query: str) -> Any:
        snapshot = await self._inner.search(query)
        self._observer["final_domain"] = urlparse(snapshot.url).hostname
        return snapshot

    async def __aexit__(self, *exc: object) -> None:
        await self._inner.__aexit__(*exc)


def observed_session_factory(
    inner_factory: Callable[[], Any], observer: dict[str, Any]
) -> Callable[[], ObservedPublicCnkiSession]:
    """service 以零参调用 session_factory，这里把内层工厂与观察器闭包进去。"""
    return lambda: ObservedPublicCnkiSession(inner_factory, observer)


def _assert_no_sensitive_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).casefold()
            if any(token in normalized for token in FORBIDDEN_FIELD_TOKENS):
                raise ValueError(f"验证证据含敏感字段：{path}.{key}")
            _assert_no_sensitive_fields(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _assert_no_sensitive_fields(child, f"{path}[{index}]")


def _evidence_payload(outcome: Any) -> dict[str, Any]:
    payload = {
        "status": outcome.status.value,
        "query": outcome.query,
        "records": [record.to_dict() for record in outcome.records],
        "incomplete_records": [record.to_dict() for record in outcome.incomplete_records],
        "excluded_non_journal_rows": outcome.excluded_non_journal_rows,
    }
    _assert_no_sensitive_fields(payload)
    for record in payload["records"]:
        if not (
            str(record["title"]).strip()
            and str(record["journal_raw"]).strip()
            and isinstance(record["publication_year"], int)
        ):
            raise ValueError("正式题录缺少篇名、期刊或可核验发表年度")
    return payload


@dataclass(frozen=True, slots=True)
class SmokeResult:
    exit_code: int
    payload: dict[str, Any]
    summary: dict[str, Any]
    message: str = ""


async def run_smoke(
    query: str, limit: int, *, session_factory: Callable[[], Any] = PublicCnkiSession
) -> SmokeResult:
    """执行一次公开检索并给出脱敏证据。session_factory 可注入，供离线回归使用。"""
    request = SearchRequest(query, limit)
    observer: dict[str, Any] = {"final_domain": None}
    service = CnkiPublicSearchService(
        session_factory=observed_session_factory(session_factory, observer)
    )
    outcome = await service.search(request.query, request.limit)
    payload = _evidence_payload(outcome)
    summary = {
        "status": outcome.status.value,
        "record_count": len(outcome.records),
        "final_domain": observer["final_domain"],
    }
    if outcome.status not in ACCEPTED_STATUSES:
        return SmokeResult(1, payload, summary, "CNKI 公开检索受限或页面合同变化；证据已保存。")
    if not 1 <= len(outcome.records) <= request.limit:
        return SmokeResult(1, payload, summary, "CNKI 公开检索未返回规定数量的正式期刊题录。")
    if observer["final_domain"] != EXPECTED_RESULT_DOMAIN:
        return SmokeResult(1, payload, summary, "CNKI 检索未到达规定的公开结果域名。")
    return SmokeResult(0, payload, summary)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CNKI 公开首页主题检索实机冒烟验证")
    parser.add_argument("--query", required=True, help="固定主题检索词")
    parser.add_argument("--limit", required=True, type=int, help="返回数量，范围为 1 至 20")
    parser.add_argument("--output", required=True, type=Path, help="脱敏 JSON 证据输出路径")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = asyncio.run(run_smoke(args.query, args.limit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result.payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result.summary, ensure_ascii=False))
    if result.message:
        print(result.message, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
