"""WebVPN 人工值守模式的批次调度与断点（环境版）。

与公开匿名模式（``PublicCnkiSession``）平级、互不影响。启用本模式需要使用者
本人以校园账号经学校官方 WebVPN 完成统一身份认证，并在整个检索期间保持浏览器
窗口打开。

三处人工介入无法自动化，是架构约束而非实现缺陷：

1. **统一身份认证**：需要校园账号密码，程序不接触凭据。
2. **登录态不能跨进程复用**：WebVPN 票据是 session cookie，导出后在新浏览器
   进程里会被服务端直接拒绝（有头/无头皆然，与 User-Agent 无关）。因此登录与
   检索必须在同一进程内完成，且不把票据写入磁盘。
3. **中途安全验证**：连续请求触发风控时需要人工滑动，程序不得自动破解。

因此本模式**不可用于定时任务或任何无人值守场景**。

本模块把「批次调度状态机」与「浏览器生命周期」分开：前者是纯逻辑，可离线测试；
后者才需要 Playwright。本文件当前只含前者。

本文件是通用版 ``cnki_search.webvpn`` 的独立移植，不导入通用版包。移植意味着
通用版的后续修正不会自动到达这里，改动时必须两边对照。
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import tempfile
import time
import unicodedata
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import (
    MAX_AUTHOR_LENGTH,
    MAX_AUTHORS,
    MAX_JOURNAL_LENGTH,
    MAX_TITLE_LENGTH,
    SearchStatus,
    is_verifiable_publication_year,
)
from .professional import ExpressionBatch

#: 实测：连续 4 次快速请求即触发安全验证，冷却约 75 秒后恢复。30 秒是据此取的
#: 保守值，**不是**二分测试得出的安全阈值，长时间高频使用仍可能触发风控。
MIN_REQUEST_INTERVAL_SECONDS = 30.0
#: 命中风控后在常规间隔之外额外等待，避免把账号推向更严的限制。
CHALLENGE_BACKOFF_SECONDS = 180.0
#: 同一批次因风控最多重试几次；超过则如实上报未完成，交由使用者决定。
MAX_CHALLENGE_RETRIES = 3

DEFAULT_LOGIN_TIMEOUT_SECONDS = 600.0
DEFAULT_POLL_INTERVAL_SECONDS = 3.0


class CheckpointPersistenceError(RuntimeError):
    """断点无法安全地原子持久化。"""


@dataclass(frozen=True, slots=True)
class WebVpnConfig:
    """WebVPN 入口配置。

    ``home_url`` 是学校 WebVPN 改写后的知网首页地址。WebVPN 对每个后端主机的
    编码不同（首页与结果页的编码主机并不一致），因此只固定首页入口，后续跳转
    交给站点自身处理，不对结果页 URL 做等值断言。
    """

    home_url: str
    login_timeout_seconds: float = DEFAULT_LOGIN_TIMEOUT_SECONDS
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS

    def __post_init__(self) -> None:
        if not self.home_url.startswith("https://"):
            raise ValueError("WebVPN 入口必须是 https 地址")
        if self.login_timeout_seconds <= 0 or self.poll_interval_seconds <= 0:
            raise ValueError("超时与轮询间隔必须为正数")


class Throttle:
    """跨进程持久的请求节流。

    时间戳必须落盘：常驻模式下模块可能被重新加载，放在模块级变量里的状态会丢，
    节流随之失效。
    """

    def __init__(self, state_file: Path, *,
                 min_interval: float = MIN_REQUEST_INTERVAL_SECONDS,
                 challenge_backoff: float = CHALLENGE_BACKOFF_SECONDS,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                 now: Callable[[], float] = time.time) -> None:
        self.state_file = state_file
        self.min_interval = min_interval
        self.challenge_backoff = challenge_backoff
        self._sleep = sleep
        self._now = now

    def _read(self) -> tuple[float, float]:
        try:
            last, backoff = self.state_file.read_text(encoding="utf-8").split()
            return float(last), float(backoff)
        except (OSError, ValueError):
            return 0.0, 0.0

    def record(self, *, challenged: bool = False) -> None:
        backoff = self.challenge_backoff if challenged else 0.0
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(f"{self._now()} {backoff}", encoding="utf-8")
        except OSError:
            pass

    async def wait(self) -> float:
        """按需等待，返回实际等待秒数。"""
        last, backoff = self._read()
        if not last:
            return 0.0
        required = self.min_interval + backoff
        elapsed = self._now() - last
        if elapsed >= required:
            return 0.0
        delay = required - elapsed
        await self._sleep(delay)
        return delay


@dataclass
class BatchCheckpoint:
    """已完成批次的断点记录。

    风控中断后从断点续跑，不重复已完成的批次——重跑既浪费限流预算，也会把
    账号更快推向风控。
    """

    state_file: Path
    completed: dict[int, dict[str, Any]] = field(default_factory=dict)

    def load(self, token: str) -> None:
        self.completed = {}
        try:
            payload = json.loads(self.state_file.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except OSError as exc:
            raise CheckpointPersistenceError(
                "无法安全读取专业检索断点"
            ) from exc
        except ValueError:
            self.save(token)
            return
        if not isinstance(payload, dict) or payload.get("token") != token:
            self.save(token)
            return
        saved = payload.get("completed", {})
        if isinstance(saved, dict):
            for key, value in saved.items():
                try:
                    index = int(key)
                except (TypeError, ValueError):
                    continue
                if isinstance(value, dict):
                    safe = _checkpoint_result(
                        value,
                        index,
                        from_payload=True,
                    )
                    if safe is not None:
                        self.completed[index] = safe
        self.save(token)

    def save(self, token: str) -> None:
        temporary: Path | None = None
        try:
            safe_completed: dict[int, dict[str, Any]] = {}
            for key, value in self.completed.items():
                if not isinstance(value, dict):
                    continue
                index = int(key)
                safe = _checkpoint_result(value, index)
                if safe is not None:
                    safe_completed[index] = safe
            payload = json.dumps(
                {"token": token, "completed": safe_completed},
                ensure_ascii=False,
            )
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.state_file.parent,
                prefix=f".{self.state_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.state_file)
            temporary = None
            self.completed = safe_completed
        except (OSError, TypeError, ValueError) as exc:
            self.completed = {}
            raise CheckpointPersistenceError(
                "无法安全写入专业检索断点"
            ) from exc
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

    def clear(self) -> None:
        self.completed = {}
        try:
            self.state_file.unlink(missing_ok=True)
        except OSError as exc:
            raise CheckpointPersistenceError(
                "无法安全清除专业检索断点"
            ) from exc


BatchExecutor = Callable[[ExpressionBatch], Awaitable[dict[str, Any]]]
ChallengeHandler = Callable[[ExpressionBatch], Awaitable[bool]]
StopPredicate = Callable[[list[dict[str, Any]]], bool]

_CHECKPOINT_RESULT_FIELDS = (
    "status",
    "index",
    "total_rows",
    "excluded_non_journal_rows",
    "records",
    "incomplete_records",
)
_CHECKPOINT_RECORD_FIELDS = (
    "title",
    "authors",
    "journal_raw",
    "publication_date",
    "publication_year",
    "document_type",
    "citations",
    "downloads",
    "is_online_first",
    "result_rank",
    "source_database",
)


def _checkpoint_text(value: str) -> str | None:
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKC", value)
        if unicodedata.category(character) not in {"Cc", "Cf"}
    ).strip()
    folded = normalized.casefold()
    if any(
        marker in folded
        for marker in (
            "su %=",
            "ly=",
            "ye between",
            "http://",
            "https://",
            "://",
            "cookie",
        )
    ):
        return None
    if "<" in normalized and ">" in normalized:
        return None
    if normalized.startswith(("/", "\\", "~")):
        return None
    if folded.startswith(("$home", "${home}", "%userprofile%")):
        return None
    if _checkpoint_windows_drive_path(normalized):
        return None
    file_scheme, separator, file_target = folded.partition(":")
    if separator and "".join(file_scheme.split()) == "file":
        file_target = file_target.lstrip()
        if file_target.startswith(("/", "\\")) or _checkpoint_windows_drive_path(
            file_target
        ):
            return None
    return normalized


def _checkpoint_windows_drive_path(value: str) -> bool:
    return (
        len(value) >= 3
        and value[0].isalpha()
        and value[1] == ":"
        and value[2] in {"\\", "/"}
    )


def _checkpoint_bibliographic_text(
    value: str,
    maximum: int,
) -> str | None:
    normalized = _checkpoint_text(value)
    if normalized is None:
        return None
    cleaned = "".join(
        character
        for character in normalized
        if unicodedata.category(character) not in {"Cc", "Cf"}
    ).strip()[:maximum]
    return _checkpoint_text(cleaned)


def _string_sequence(value: Any) -> list[str] | None:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or any(not isinstance(item, str) for item in value)
    ):
        return None
    authors: list[str] = []
    for item in value[:MAX_AUTHORS]:
        cleaned = _checkpoint_bibliographic_text(item, MAX_AUTHOR_LENGTH)
        if cleaned is None:
            return None
        if cleaned:
            authors.append(cleaned)
    return authors


def _checkpoint_record(
    record: Any,
    *,
    formal: bool,
) -> dict[str, Any] | None:
    if hasattr(record, "to_dict"):
        source = record.to_dict()
    elif isinstance(record, Mapping):
        source = dict(record)
    else:
        return None
    required_strings = (
        "title",
        "journal_raw",
        "publication_date",
        "document_type",
        "source_database",
    )
    if any(not isinstance(source.get(name), str) for name in required_strings):
        return None
    title = _checkpoint_bibliographic_text(
        source["title"],
        MAX_TITLE_LENGTH,
    )
    journal = _checkpoint_bibliographic_text(
        source["journal_raw"],
        MAX_JOURNAL_LENGTH,
    )
    publication_date = _checkpoint_text(source["publication_date"])
    document_type = _checkpoint_text(source["document_type"])
    source_database = _checkpoint_text(source["source_database"])
    if any(
        value is None
        for value in (
            title,
            journal,
            publication_date,
            document_type,
            source_database,
        )
    ):
        return None
    if document_type != "期刊" or source_database != "CNKI":
        return None
    authors = _string_sequence(source.get("authors"))
    if authors is None:
        return None
    safe: dict[str, Any] = {
        "title": title,
        "journal_raw": journal,
        "publication_date": publication_date,
        "document_type": document_type,
        "source_database": source_database,
    }
    safe["authors"] = authors
    for name in ("publication_year", "citations", "downloads"):
        value = source.get(name)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            return None
        if name in {"citations", "downloads"} and value is not None and value < 0:
            return None
        safe[name] = value
    complete_bibliography = (
        bool(safe["title"])
        and bool(safe["journal_raw"])
        and is_verifiable_publication_year(safe["publication_year"])
    )
    if formal != complete_bibliography:
        return None
    result_rank = source.get("result_rank")
    if (
        not isinstance(result_rank, int)
        or isinstance(result_rank, bool)
        or result_rank < 0
    ):
        return None
    safe["result_rank"] = result_rank
    for name in ("is_online_first",):
        value = source.get(name)
        if not isinstance(value, bool):
            return None
        safe[name] = value
    return {
        name: safe[name]
        for name in _CHECKPOINT_RECORD_FIELDS
        if name in safe
    }


def _checkpoint_records(
    value: Any,
    *,
    formal: bool,
    require_list: bool,
) -> list[dict[str, Any]] | None:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or (require_list and not isinstance(value, list))
    ):
        return None
    records: list[dict[str, Any]] = []
    for record in value:
        safe = _checkpoint_record(record, formal=formal)
        if safe is None:
            return None
        records.append(safe)
    return records


def _checkpoint_result(
    result: dict[str, Any],
    index: int,
    *,
    from_payload: bool = False,
) -> dict[str, Any] | None:
    status = result.get("status")
    total_rows = result.get("total_rows", 0)
    excluded = result.get("excluded_non_journal_rows", 0)
    records_value = result.get("records") if from_payload else result.get(
        "records", ()
    )
    incomplete_value = result.get(
        "incomplete_records",
        [] if from_payload else (),
    )
    records = _checkpoint_records(
        records_value,
        formal=True,
        require_list=from_payload,
    )
    incomplete = _checkpoint_records(
        incomplete_value,
        formal=False,
        require_list=from_payload,
    )
    if (
        status not in {
            SearchStatus.SUCCESS.value,
            SearchStatus.NO_RESULTS.value,
        }
        or not isinstance(total_rows, int)
        or isinstance(total_rows, bool)
        or not isinstance(excluded, int)
        or isinstance(excluded, bool)
        or total_rows < 0
        or excluded < 0
        or excluded > total_rows
        or records is None
        or incomplete is None
    ):
        return None
    if excluded + len(records) + len(incomplete) > total_rows:
        return None
    if status == SearchStatus.NO_RESULTS.value and (
        total_rows != 0
        or excluded != 0
        or records
        or incomplete
    ):
        return None
    safe = {
        "status": status,
        "index": index,
        "total_rows": total_rows,
        "excluded_non_journal_rows": excluded,
        "records": records,
        "incomplete_records": incomplete,
    }
    return {name: safe[name] for name in _CHECKPOINT_RESULT_FIELDS}


def _restore_checkpoint_result(
    result: dict[str, Any],
    batch: ExpressionBatch,
) -> dict[str, Any]:
    from .models import PaperRecord

    restored: dict[str, Any] = {
        "status": result.get("status"),
        "index": result.get("index", batch.index),
        "total_rows": result.get("total_rows", 0),
        "excluded_non_journal_rows": result.get(
            "excluded_non_journal_rows", 0
        ),
    }
    for name in ("records", "incomplete_records"):
        records: list[PaperRecord] = []
        for saved in result.get(name, ()):
            if not isinstance(saved, dict):
                continue
            values = {
                field: saved[field]
                for field in _CHECKPOINT_RECORD_FIELDS
                if field in saved
            }
            values["search_query"] = batch.expression
            try:
                records.append(PaperRecord(**values))
            except (TypeError, ValueError):
                continue
        restored[name] = tuple(records)
    return {
        name: restored[name]
        for name in _CHECKPOINT_RESULT_FIELDS
    }


async def run_batches(
    batches: Sequence[ExpressionBatch],
    execute: BatchExecutor,
    *,
    on_challenge: ChallengeHandler | None = None,
    checkpoint: BatchCheckpoint | None = None,
    throttle: Throttle | None = None,
    max_challenge_retries: int = MAX_CHALLENGE_RETRIES,
    should_stop: StopPredicate | None = None,
) -> dict[str, Any]:
    """依次执行各批次，遇安全验证则暂停等待人工处理后续跑。

    ``on_challenge`` 返回 ``True`` 表示人工已完成验证、可以重试当前批次；
    返回 ``False`` 表示放弃，此时如实上报未完成批次而不是假装成功。
    """
    if not batches:
        raise ValueError("批次列表不能为空")
    token = hashlib.sha256(
        "\n".join(batch.expression for batch in batches).encode("utf-8")
    ).hexdigest()
    if checkpoint is not None:
        try:
            checkpoint.load(token)
        except CheckpointPersistenceError as exc:
            return _summary(
                [],
                batches,
                token,
                None,
                False,
                stopped_at=batches[0],
                stopped_result={
                    "status": SearchStatus.CONFIGURATION_ERROR.value,
                    "detail": str(exc),
                },
                terminal_status=SearchStatus.CONFIGURATION_ERROR.value,
            )

    results: list[dict[str, Any]] = []
    human_intervention_required = False
    for batch in batches:
        if checkpoint is not None and batch.index in checkpoint.completed:
            results.append(
                _restore_checkpoint_result(
                    checkpoint.completed[batch.index],
                    batch,
                )
            )
            if should_stop is not None and should_stop(results):
                return _summary(
                    results,
                    batches,
                    token,
                    checkpoint,
                    human_intervention_required,
                    limit_reached=True,
                )
            continue

        challenge_attempts = 0
        network_retries = 0
        while True:
            if throttle is not None:
                await throttle.wait()
            result = await execute(batch)
            status = result.get("status")
            challenged = status == SearchStatus.CHALLENGE_DETECTED.value
            if throttle is not None:
                throttle.record(challenged=challenged)
            if challenged:
                human_intervention_required = True
                challenge_attempts += 1
                if (
                    on_challenge is None
                    or challenge_attempts > max_challenge_retries
                ):
                    return _summary(
                        results,
                        batches,
                        token,
                        checkpoint,
                        human_intervention_required,
                        stopped_at=batch,
                        stopped_result=result,
                        terminal_status=SearchStatus.CHALLENGE_DETECTED.value,
                    )
                if not await on_challenge(batch):
                    return _summary(
                        results,
                        batches,
                        token,
                        checkpoint,
                        human_intervention_required,
                        stopped_at=batch,
                        stopped_result=result,
                        terminal_status=SearchStatus.CHALLENGE_DETECTED.value,
                    )
                continue
            if status == SearchStatus.NETWORK_ERROR.value and network_retries < 1:
                network_retries += 1
                continue
            if status not in {
                SearchStatus.SUCCESS.value,
                SearchStatus.NO_RESULTS.value,
            }:
                return _summary(
                    results,
                    batches,
                    token,
                    checkpoint,
                    human_intervention_required,
                    stopped_at=batch,
                    stopped_result=result,
                    terminal_status=status,
                )
            break

        results.append(result)
        if checkpoint is not None:
            safe = _checkpoint_result(
                result,
                batch.index,
            )
            if safe is None:
                checkpoint.completed = {}
                return _summary(
                    [],
                    batches,
                    token,
                    None,
                    human_intervention_required,
                    stopped_at=batch,
                    stopped_result={
                        "status": SearchStatus.CONFIGURATION_ERROR.value,
                        "detail": "批次结果无法安全写入专业检索断点",
                    },
                    terminal_status=SearchStatus.CONFIGURATION_ERROR.value,
                )
            checkpoint.completed[batch.index] = safe
            try:
                checkpoint.save(token)
            except CheckpointPersistenceError as exc:
                return _summary(
                    [],
                    batches,
                    token,
                    None,
                    human_intervention_required,
                    stopped_at=batch,
                    stopped_result={
                        "status": SearchStatus.CONFIGURATION_ERROR.value,
                        "detail": str(exc),
                    },
                    terminal_status=SearchStatus.CONFIGURATION_ERROR.value,
                )
        if (
            status == SearchStatus.SUCCESS.value
            and should_stop is not None
            and should_stop(results)
        ):
            return _summary(
                results,
                batches,
                token,
                checkpoint,
                human_intervention_required,
                limit_reached=True,
            )

    if checkpoint is not None:
        try:
            checkpoint.clear()
        except CheckpointPersistenceError as exc:
            return _summary(
                [],
                batches,
                token,
                None,
                human_intervention_required,
                stopped_at=batches[-1],
                stopped_result={
                    "status": SearchStatus.CONFIGURATION_ERROR.value,
                    "detail": str(exc),
                },
                terminal_status=SearchStatus.CONFIGURATION_ERROR.value,
            )
    return _summary(results, batches, token, checkpoint, human_intervention_required)


def _summary(results: list[dict[str, Any]], batches: Sequence[ExpressionBatch],
             token: str, checkpoint: BatchCheckpoint | None,
             human_intervention_required: bool,
             stopped_at: ExpressionBatch | None = None,
             stopped_result: dict[str, Any] | None = None,
             limit_reached: bool = False,
             terminal_status: str | None = None) -> dict[str, Any]:
    if stopped_at is not None and checkpoint is not None:
        try:
            checkpoint.save(token)
        except CheckpointPersistenceError as exc:
            results = []
            limit_reached = False
            terminal_status = SearchStatus.CONFIGURATION_ERROR.value
            stopped_result = {
                "status": terminal_status,
                "detail": str(exc),
            }
    public_stopped_result = None
    if stopped_result is not None:
        public_stopped_result = {
            name: stopped_result[name]
            for name in ("status", "index", "detail")
            if name in stopped_result
        }
    return {
        "batches_completed": len(results),
        "batches_total": len(batches),
        "complete": stopped_at is None,
        "stopped_at_batch": stopped_at.index if stopped_at is not None else None,
        "stopped_result": public_stopped_result,
        "human_intervention_required": human_intervention_required,
        "limit_reached": limit_reached,
        "terminal_status": terminal_status,
        "results": results,
    }
