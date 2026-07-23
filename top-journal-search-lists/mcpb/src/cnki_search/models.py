from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any


class SearchStatus(StrEnum):
    SUCCESS = "success"
    NO_RESULTS = "no_results"
    PARTIAL = "partial"
    RATE_LIMITED = "rate_limited"
    CHALLENGE_DETECTED = "challenge_detected"
    LOGIN_REQUIRED = "login_required"
    FORBIDDEN = "forbidden"
    PAGE_CONTRACT_CHANGED = "page_contract_changed"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"


@dataclass(frozen=True, slots=True)
class SearchRequest:
    query: str
    limit: int = 20

    def __post_init__(self) -> None:
        # 与 cache.normalize_cache_query 使用同一套空白折叠口径，否则
        # "数字化  转型" 与 "数字化 转型" 会命中同一缓存项，却返回另一次
        # 请求的 query 字面量，造成返回值与本次请求不一致。
        normalized = " ".join(unicodedata.normalize("NFKC", self.query).split())
        if not normalized:
            raise ValueError("主题检索词不能为空")
        if not 1 <= self.limit <= 20:
            raise ValueError("返回数量必须为 1 到 20")
        object.__setattr__(self, "query", normalized)


@dataclass(slots=True)
class PaperRecord:
    title: str
    authors: list[str]
    journal_raw: str
    publication_date: str
    publication_year: int | None
    document_type: str
    citations: int | None
    downloads: int | None
    is_online_first: bool
    result_rank: int
    source_database: str
    search_query: str
    journal_matched_title: str | None = None
    journal_match_status: str = "unmatched"
    journal_match_method: str | None = None
    priority_level: int | None = None
    priority_group: str | None = None
    source_catalogs: list[str] = field(default_factory=list)
    subject_categories: list[str] = field(default_factory=list)
    ncs_internal_rank: int | None = None
    catalog_version: str = field(default="2026-07-15", init=False)
    manual_review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchOutcome:
    status: SearchStatus
    query: str
    records: list[PaperRecord]
    incomplete_records: list[PaperRecord]
    excluded_non_journal_rows: int
    warnings: list[str]
    searched_at: str

    def __post_init__(self) -> None:
        if any(not _has_complete_bibliography(record) for record in self.records):
            raise ValueError("正式题录必须具有篇名、期刊和可核验发表年度")
        if any(_has_complete_bibliography(record) for record in self.incomplete_records):
            raise ValueError("不完整题录集合不能包含完整题录")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.status
            in {SearchStatus.SUCCESS, SearchStatus.NO_RESULTS, SearchStatus.PARTIAL},
            "status": self.status.value,
            "query": self.query,
            "records": [record.to_dict() for record in self.records],
            "incomplete_records": [record.to_dict() for record in self.incomplete_records],
            "excluded_non_journal_rows": self.excluded_non_journal_rows,
            "warnings": list(self.warnings),
            "searched_at": self.searched_at,
        }


def _has_complete_bibliography(record: PaperRecord) -> bool:
    return (
        bool(record.title.strip())
        and bool(record.journal_raw.strip())
        and isinstance(record.publication_year, int)
        and not isinstance(record.publication_year, bool)
        and is_verifiable_publication_year(record.publication_year)
    )


def is_verifiable_publication_year(value: int | None) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 1900 <= value <= date.today().year + 1
