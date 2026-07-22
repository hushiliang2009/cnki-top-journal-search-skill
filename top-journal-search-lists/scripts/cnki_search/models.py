from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class SessionStatus(StrEnum):
    LOGIN_REQUIRED = "login_required"
    WAITING_FOR_USER = "waiting_for_user"
    READY = "ready"
    CAPTCHA = "captcha"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMITED = "rate_limited"
    SESSION_EXPIRED = "session_expired"
    CLOSED = "closed"


class SearchMode(StrEnum):
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    AUTHOR = "author"
    SENTENCE = "sentence"


@dataclass(slots=True)
class SearchRequest:
    mode: SearchMode
    query: str
    pages: int = 1
    fields: list[dict[str, Any]] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.query.strip() and not self.fields:
            raise ValueError("检索式或检索字段不能为空")
        if not 1 <= self.pages <= 3:
            raise ValueError("检索页数必须为 1 到 3")


@dataclass(slots=True)
class PaperRecord:
    title: str
    authors: list[str] = field(default_factory=list)
    first_author: str = ""
    affiliations: list[str] = field(default_factory=list)
    journal: str = ""
    year: int | None = None
    volume: str = ""
    issue: str = ""
    pages: str = ""
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    funds: list[str] = field(default_factory=list)
    doi: str = ""
    detail_url: str = ""
    source_mode: str = ""
    searched_at: str = ""
    download_status: str = "not_requested"
    journal_level: str = "未匹配"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ToolResponse:
    ok: bool
    status: SessionStatus
    message: str = ""
    data: Any = None
    warnings: list[str] = field(default_factory=list)
    next_action: str | None = None

    @classmethod
    def success(cls, status: SessionStatus, data: Any = None) -> "ToolResponse":
        return cls(ok=True, status=status, data=data)

    @classmethod
    def failure(
        cls,
        status: SessionStatus,
        message: str,
        *,
        next_action: str | None = None,
    ) -> "ToolResponse":
        return cls(ok=False, status=status, message=message, next_action=next_action)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "warnings": list(self.warnings),
            "next_action": self.next_action,
        }

