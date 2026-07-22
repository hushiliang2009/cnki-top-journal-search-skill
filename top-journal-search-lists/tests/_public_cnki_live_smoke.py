from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cnki_search.models import SearchRequest, SearchStatus
from cnki_search.service import CnkiPublicSearchService
from cnki_search.session import PublicCnkiSession


FORBIDDEN_FIELD_TOKENS = ("url", "cookie", "token", "session")
ACCEPTED_STATUSES = {SearchStatus.SUCCESS, SearchStatus.PARTIAL}


class ObservedPublicCnkiSession:
    """仅在进程内保留最终页面域名，避免把 URL 写入验证证据。"""

    final_domain: str | None = None

    def __init__(self) -> None:
        self._session = PublicCnkiSession()

    def __enter__(self) -> "ObservedPublicCnkiSession":
        self._session.__enter__()
        return self

    def search(self, query: str) -> Any:
        snapshot = self._session.search(query)
        self.__class__.final_domain = urlparse(snapshot.url).hostname
        return snapshot

    def __exit__(self, *exc: object) -> None:
        self._session.__exit__(*exc)


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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CNKI 公开首页主题检索实机冒烟验证")
    parser.add_argument("--query", required=True, help="固定主题检索词")
    parser.add_argument("--limit", required=True, type=int, help="返回数量，范围为 1 至 20")
    parser.add_argument("--output", required=True, type=Path, help="脱敏 JSON 证据输出路径")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    request = SearchRequest(args.query, args.limit)
    ObservedPublicCnkiSession.final_domain = None
    outcome = CnkiPublicSearchService(session_factory=ObservedPublicCnkiSession).search(
        request.query, request.limit
    )
    payload = _evidence_payload(outcome)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": outcome.status.value,
        "record_count": len(outcome.records),
        "final_domain": ObservedPublicCnkiSession.final_domain,
    }
    print(json.dumps(summary, ensure_ascii=False))
    if outcome.status not in ACCEPTED_STATUSES:
        print("CNKI 公开检索受限或页面合同变化；证据已保存，Task 8 未完成。", file=sys.stderr)
        return 1
    if not 1 <= len(outcome.records) <= request.limit:
        print("CNKI 公开检索未返回规定数量的正式期刊题录。", file=sys.stderr)
        return 1
    if ObservedPublicCnkiSession.final_domain != "kns.cnki.net":
        print("CNKI 检索未到达规定的公开结果域名。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
