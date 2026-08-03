import asyncio
import json
import os
from pathlib import Path

import pytest

from cnki_search import webvpn
from cnki_search.models import PaperRecord, SearchStatus
from cnki_search.professional import (
    ExpressionBatch,
    SourceCategorySpec,
    build_batches,
    build_expression,
)


def _batches(count: int):
    """构造恰好 count 个批次：刊名等长，预算取单刊表达式长度，故一批一刊。"""
    journals = [f"测试期刊{index:03d}" for index in range(count)]
    budget = len(build_expression("数字经济", journals[:1]))
    batches = build_batches("数字经济", journals, max_chars=budget)
    assert len(batches) == count
    return batches


def _ok(batch) -> dict:
    return {"status": SearchStatus.SUCCESS.value, "batch": batch.index}


def _challenge(batch) -> dict:
    return {"status": SearchStatus.CHALLENGE_DETECTED.value, "batch": batch.index}


def _record(batch, *, title: str = "数字经济研究") -> dict:
    return PaperRecord(
        title=title,
        authors=["张三"],
        journal_raw="管理世界",
        publication_date="2025-03-11",
        publication_year=2025,
        document_type="期刊",
        citations=3,
        downloads=5,
        is_online_first=False,
        result_rank=1,
        source_database="CNKI",
        search_query=batch.expression,
    ).to_dict()


# ── 配置校验 ────────────────────────────────────────────────────────────────

def test_config_requires_https_entry_and_positive_timers() -> None:
    with pytest.raises(ValueError):
        webvpn.WebVpnConfig("http://webvpn.example.edu.cn/")
    with pytest.raises(ValueError):
        webvpn.WebVpnConfig("https://webvpn.example.edu.cn/", login_timeout_seconds=0)


# ── 批次调度 ────────────────────────────────────────────────────────────────

def test_all_batches_run_in_order_when_nothing_blocks() -> None:
    batches = _batches(3)
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(webvpn.run_batches(batches, execute))
    assert seen == [1, 2, 3]
    assert summary["complete"] is True
    assert summary["batches_completed"] == summary["batches_total"] == 3
    assert summary["human_intervention_required"] is False
    assert summary["limit_reached"] is False
    assert summary["terminal_status"] is None


def test_limit_stops_before_submitting_remaining_batches() -> None:
    batches = _batches(3)
    executor_calls: list[int] = []

    async def execute(batch):
        executor_calls.append(batch.index)
        return {
            "status": SearchStatus.SUCCESS.value,
            "records": [_record(batch)],
        }

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            should_stop=lambda results: len(results) == 1,
        )
    )

    assert summary["limit_reached"] is True
    assert summary["batches_completed"] == 1
    assert summary["complete"] is True
    assert summary["terminal_status"] is None
    assert executor_calls == [1]


def test_challenge_pauses_for_human_then_resumes_the_same_batch() -> None:
    batches = _batches(2)
    attempts: list[int] = []
    prompted: list[int] = []

    async def execute(batch):
        attempts.append(batch.index)
        # 第 2 批第一次撞风控，人工处理后重试成功
        if batch.index == 2 and attempts.count(2) == 1:
            return _challenge(batch)
        return _ok(batch)

    async def on_challenge(batch):
        prompted.append(batch.index)
        return True

    summary = asyncio.run(webvpn.run_batches(batches, execute, on_challenge=on_challenge))
    assert prompted == [2]
    assert attempts == [1, 2, 2]
    assert summary["complete"] is True
    assert summary["human_intervention_required"] is True


def test_giving_up_reports_incomplete_rather_than_pretending_success() -> None:
    batches = _batches(3)

    async def execute(batch):
        return _challenge(batch) if batch.index == 2 else _ok(batch)

    async def on_challenge(_batch):
        return False        # 使用者选择放弃

    summary = asyncio.run(webvpn.run_batches(batches, execute, on_challenge=on_challenge))
    assert summary["complete"] is False
    assert summary["stopped_at_batch"] == 2
    assert summary["batches_completed"] == 1
    assert summary["human_intervention_required"] is True


def test_repeated_challenges_stop_after_retry_budget() -> None:
    batches = _batches(1)
    attempts = 0

    async def execute(batch):
        nonlocal attempts
        attempts += 1
        return _challenge(batch)

    async def on_challenge(_batch):
        return True

    summary = asyncio.run(webvpn.run_batches(
        batches, execute, on_challenge=on_challenge, max_challenge_retries=2))
    assert summary["complete"] is False
    assert attempts == 3            # 首次 + 2 次重试
    assert summary["batches_completed"] == 0


def test_without_handler_a_challenge_stops_immediately() -> None:
    batches = _batches(2)

    async def execute(batch):
        return _challenge(batch)

    summary = asyncio.run(webvpn.run_batches(batches, execute))
    assert summary["complete"] is False and summary["stopped_at_batch"] == 1


def test_page_contract_change_stops_before_later_batches() -> None:
    batches = _batches(2)
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return {
            "status": SearchStatus.PAGE_CONTRACT_CHANGED.value,
            "batch": batch.index,
            "detail": "结果表结构变化",
        }

    summary = asyncio.run(webvpn.run_batches(batches, execute))

    assert seen == [1]
    assert summary["complete"] is False
    assert summary["stopped_at_batch"] == 1
    assert summary["batches_completed"] == 0
    assert summary["stopped_result"]["status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert summary["limit_reached"] is False
    assert summary["terminal_status"] == SearchStatus.PAGE_CONTRACT_CHANGED.value


@pytest.mark.parametrize(
    "status",
    [
        SearchStatus.NO_DATA_RETRY_LATER,
        SearchStatus.FORBIDDEN,
        SearchStatus.RATE_LIMITED,
    ],
)
def test_terminal_status_stops_before_later_batches(status: SearchStatus) -> None:
    batches = _batches(2)
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return {"status": status.value, "batch": batch.index}

    summary = asyncio.run(webvpn.run_batches(batches, execute))

    assert seen == [1]
    assert summary["complete"] is False
    assert summary["batches_completed"] == 0
    assert summary["terminal_status"] == status.value
    assert summary["limit_reached"] is False


def test_no_results_is_completed_and_later_batches_continue() -> None:
    batches = _batches(2)
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        if batch.index == 1:
            return {"status": SearchStatus.NO_RESULTS.value, "records": []}
        return _ok(batch)

    summary = asyncio.run(webvpn.run_batches(batches, execute))

    assert seen == [1, 2]
    assert summary["complete"] is True
    assert summary["batches_completed"] == 2
    assert summary["terminal_status"] is None


def test_network_error_retries_once_with_fresh_throttle_wait() -> None:
    batches = _batches(2)
    attempts: list[int] = []

    class CountingThrottle:
        def __init__(self) -> None:
            self.wait_calls = 0

        async def wait(self) -> float:
            self.wait_calls += 1
            return 0.0

        def record(self, *, challenged: bool = False) -> None:
            assert challenged is False

    throttle = CountingThrottle()

    async def execute(batch):
        attempts.append(batch.index)
        return {"status": SearchStatus.NETWORK_ERROR.value}

    summary = asyncio.run(
        webvpn.run_batches(batches, execute, throttle=throttle)
    )

    assert attempts == [1, 1]
    assert throttle.wait_calls == 2
    assert summary["batches_completed"] == 0
    assert summary["terminal_status"] == SearchStatus.NETWORK_ERROR.value
    assert summary["limit_reached"] is False


def test_empty_batch_list_is_rejected() -> None:
    async def execute(batch):
        return _ok(batch)

    with pytest.raises(ValueError):
        asyncio.run(webvpn.run_batches([], execute))


# ── 断点续跑 ────────────────────────────────────────────────────────────────

def test_completed_batches_are_not_rerun_after_resume(tmp_path: Path) -> None:
    """重跑已完成批次既浪费限流预算，也会更快把账号推向风控。"""
    batches = _batches(3)
    checkpoint = webvpn.BatchCheckpoint(tmp_path / "progress.json")
    first_pass: list[int] = []

    async def failing(batch):
        first_pass.append(batch.index)
        return _challenge(batch) if batch.index == 3 else _ok(batch)

    asyncio.run(webvpn.run_batches(batches, failing, checkpoint=checkpoint))
    assert first_pass == [1, 2, 3]

    second_pass: list[int] = []

    async def succeeding(batch):
        second_pass.append(batch.index)
        return _ok(batch)

    resumed = webvpn.BatchCheckpoint(tmp_path / "progress.json")
    summary = asyncio.run(webvpn.run_batches(batches, succeeding, checkpoint=resumed))
    assert second_pass == [3]                 # 仅重跑未完成的那一批
    assert summary["complete"] is True
    assert summary["batches_completed"] == 3


def test_checkpoint_is_discarded_when_the_query_changes(tmp_path: Path) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)

    async def execute(batch):
        return _challenge(batch) if batch.index == 2 else _ok(batch)

    asyncio.run(webvpn.run_batches(batches, execute, checkpoint=webvpn.BatchCheckpoint(state)))

    other = build_batches("共同富裕", ["经济研究", "管理世界"])
    seen: list[int] = []

    async def execute_other(batch):
        seen.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(webvpn.run_batches(
        other, execute_other, checkpoint=webvpn.BatchCheckpoint(state)))
    assert seen == [1]                        # 换了检索条件，旧断点不得复用
    assert summary["complete"] is True


# ── 断点身份 ────────────────────────────────────────────────────────────────

def _identity_batch(expression: str, scope_id: str, topic_field: str,
                    category: SourceCategorySpec | None, *,
                    catalog_version: str = "2026-07-15") -> ExpressionBatch:
    return ExpressionBatch(
        index=1,
        total=1,
        journals=(),
        expression=expression,
        scope_id=scope_id,
        catalog_version=catalog_version,
        topic_field=topic_field,
        source_category=category,
    )


def test_same_expression_with_cssci_and_pku_facets_has_distinct_tokens() -> None:
    """同一表达式配不同分面是两次不同检索，断点不得互相复用。"""
    cssci = _identity_batch(
        "TI %= '气候'", "cssci", "TI", SourceCategorySpec("P0209", "CSSCI"),
    )
    pku = _identity_batch(
        "TI %= '气候'", "pku_core", "TI", SourceCategorySpec("P01", "北大核心"),
    )
    assert webvpn._checkpoint_token([cssci]) != webvpn._checkpoint_token([pku])


def test_same_expression_in_different_fields_or_scopes_has_distinct_tokens() -> None:
    assert webvpn._checkpoint_token([_identity_batch("X", "scope-a", "TI", None)]) != \
        webvpn._checkpoint_token([_identity_batch("X", "scope-a", "SU", None)])
    assert webvpn._checkpoint_token([_identity_batch("X", "scope-a", "TI", None)]) != \
        webvpn._checkpoint_token([_identity_batch("X", "scope-b", "TI", None)])


def test_same_scope_and_expression_in_different_catalog_versions_has_distinct_tokens() -> None:
    assert webvpn._checkpoint_token(
        [_identity_batch("X", "scope-a", "TI", None, catalog_version="3.0")]
    ) != webvpn._checkpoint_token(
        [_identity_batch("X", "scope-a", "TI", None, catalog_version="4.0")]
    )


def test_checkpoint_token_is_a_sha256_digest_and_never_leaks_the_expression() -> None:
    token = webvpn._checkpoint_token(
        [_identity_batch("TI %= '气候'", "cssci", "TI", None)]
    )
    assert len(token) == 64
    assert set(token) <= set("0123456789abcdef")
    assert "气候" not in token


def test_run_batches_uses_the_full_identity_token(tmp_path: Path) -> None:
    """run_batches 不得再内联只哈希表达式的旧算法。"""
    state = tmp_path / "progress.json"
    batches = _batches(2)

    async def execute(batch):
        return _challenge(batch) if batch.index == 2 else _ok(batch)

    asyncio.run(webvpn.run_batches(
        batches, execute, checkpoint=webvpn.BatchCheckpoint(state),
    ))

    payload = json.loads(state.read_text(encoding="utf-8"))
    assert payload["token"] == webvpn._checkpoint_token(batches)


def test_checkpoint_record_whitelist_carries_field_and_group_matches() -> None:
    """字段与分组命中信息属于可安全落盘的检索身份，链接与 DOI 仍禁止。"""
    assert {
        "topic_match_field", "matched_topic_fields", "matched_search_groups",
    } <= set(webvpn._CHECKPOINT_RECORD_FIELDS)
    for forbidden in ("doi", "detail_url", "download_url", "pdf_url", "html",
                      "result_url", "search_query"):
        assert forbidden not in webvpn._CHECKPOINT_RECORD_FIELDS


def _matched_record(batch) -> dict:
    record = _record(batch)
    record["topic_match_field"] = "SU"
    record["matched_topic_fields"] = ["TI", "SU"]
    record["matched_search_groups"] = ["cssci"]
    return record


def test_match_metadata_survives_a_checkpoint_round_trip(tmp_path: Path) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)

    async def interrupted(batch):
        if batch.index == 2:
            return _challenge(batch)
        return {
            "status": SearchStatus.SUCCESS.value,
            "index": batch.index,
            "total_rows": 1,
            "excluded_non_journal_rows": 0,
            "records": [_matched_record(batch)],
            "incomplete_records": [],
        }

    asyncio.run(webvpn.run_batches(
        batches, interrupted, checkpoint=webvpn.BatchCheckpoint(state),
    ))

    saved = json.loads(state.read_text(encoding="utf-8"))["completed"]["1"]["records"][0]
    assert saved["topic_match_field"] == "SU"
    assert saved["matched_topic_fields"] == ["TI", "SU"]
    assert saved["matched_search_groups"] == ["cssci"]

    async def resumed(batch):
        return {
            "status": SearchStatus.SUCCESS.value,
            "index": batch.index,
            "records": [],
            "incomplete_records": [],
        }

    summary = asyncio.run(webvpn.run_batches(
        batches, resumed, checkpoint=webvpn.BatchCheckpoint(state),
        should_stop=lambda results: len(results) == 1,
    ))
    restored = summary["results"][0]["records"][0]
    assert isinstance(restored, PaperRecord)
    assert restored.topic_match_field == "SU"
    assert restored.matched_topic_fields == ["TI", "SU"]
    assert restored.matched_search_groups == ["cssci"]


@pytest.mark.parametrize(
    "poisoned",
    [
        {"topic_match_field": "AB"},
        {"topic_match_field": 1},
        {"matched_topic_fields": ["TI", "AB"]},
        {"matched_topic_fields": "TI"},
        {"matched_search_groups": ["cssci\u0007"]},
        {"matched_search_groups": [{"group": "cssci"}]},
    ],
)
def test_checkpoint_rejects_unsafe_match_metadata(
    tmp_path: Path, poisoned: dict,
) -> None:
    """守卫失败关闭：非受控字段名或含控制字符的分组名不得落盘。"""
    state = tmp_path / "progress.json"
    batches = _batches(2)

    async def execute(batch):
        if batch.index == 2:
            return _challenge(batch)
        record = _record(batch)
        record.update(poisoned)
        return {
            "status": SearchStatus.SUCCESS.value,
            "index": batch.index,
            "total_rows": 1,
            "excluded_non_journal_rows": 0,
            "records": [record],
            "incomplete_records": [],
        }

    asyncio.run(webvpn.run_batches(
        batches, execute, checkpoint=webvpn.BatchCheckpoint(state),
    ))

    if state.exists():
        payload = json.loads(state.read_text(encoding="utf-8"))
        assert payload["completed"] == {}


def test_checkpoint_contains_no_expression_url_html_cookie_or_path(
    tmp_path: Path,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)

    async def execute(batch):
        if batch.index == 2:
            return _challenge(batch)
        return {
            "status": SearchStatus.SUCCESS.value,
            "index": batch.index,
            "total_rows": 1,
            "excluded_non_journal_rows": 0,
            "records": [_record(batch)],
            "incomplete_records": [],
            "result_url": "https://webvpn.example.edu.cn/result",
            "html": "<table>secret</table>",
            "cookie": "ticket=secret",
            "profile_path": "C:\\Users\\example\\profile",
        }

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    text = state.read_text(encoding="utf-8")
    payload = json.loads(text)
    assert payload["token"] == webvpn._checkpoint_token(batches)
    assert set(payload["completed"]["1"]) == {
        "status",
        "index",
        "total_rows",
        "excluded_non_journal_rows",
        "records",
        "incomplete_records",
    }
    for forbidden in (
        "SU %=",
        "https://",
        "<table",
        "cookie",
        "profile_path",
        "C:\\Users",
    ):
        assert forbidden.casefold() not in text.casefold()


def test_checkpoint_records_are_restored_as_paper_records(tmp_path: Path) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)

    async def interrupted(batch):
        if batch.index == 2:
            return _challenge(batch)
        return {
            "status": SearchStatus.SUCCESS.value,
            "index": batch.index,
            "total_rows": 1,
            "excluded_non_journal_rows": 0,
            "records": [_record(batch)],
            "incomplete_records": [],
        }

    asyncio.run(
        webvpn.run_batches(
            batches,
            interrupted,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    async def resumed(batch):
        return {
            "status": SearchStatus.SUCCESS.value,
            "index": batch.index,
            "records": [],
            "incomplete_records": [],
        }

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            resumed,
            checkpoint=webvpn.BatchCheckpoint(state),
            should_stop=lambda results: len(results) == 1,
        )
    )

    record = summary["results"][0]["records"][0]
    assert isinstance(record, PaperRecord)
    assert record.search_query == batches[0].expression


def test_checkpoint_resave_sanitizes_loaded_completed_payload(tmp_path: Path) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [_record(batches[0])],
                        "result_url": "https://example.invalid/result",
                        "cookie": "ticket=secret",
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    async def execute(batch):
        return _challenge(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    text = state.read_text(encoding="utf-8")
    for forbidden in ("SU %=", "https://", "cookie"):
        assert forbidden.casefold() not in text.casefold()


def test_loaded_checkpoint_is_sanitized_before_immediate_limit_return(
    tmp_path: Path,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [_record(batches[0])],
                        "expression": batches[0].expression,
                        "result_url": "https://example.invalid/result",
                        "html": "<table>secret</table>",
                        "cookie": "ticket=secret",
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    executor_calls: list[int] = []

    async def execute(batch):
        executor_calls.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
            should_stop=lambda results: bool(results[0]["records"]),
        )
    )

    assert executor_calls == []
    assert set(summary["results"][0]) == {
        "status",
        "index",
        "total_rows",
        "excluded_non_journal_rows",
        "records",
        "incomplete_records",
    }
    text = state.read_text(encoding="utf-8")
    for forbidden in ("SU %=", "https://", "<table", "cookie"):
        assert forbidden.casefold() not in text.casefold()


@pytest.mark.parametrize(
    "existing_file",
    ["missing", "corrupt", "token_mismatch"],
)
def test_checkpoint_load_always_discards_in_memory_state_before_new_query(
    tmp_path: Path,
    existing_file: str,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    checkpoint = webvpn.BatchCheckpoint(state)
    checkpoint.completed = {
        1: {
            "status": SearchStatus.SUCCESS.value,
            "index": 1,
            "records": [_record(batches[0])],
        }
    }
    if existing_file == "corrupt":
        state.write_text("{not-json", encoding="utf-8")
    elif existing_file == "token_mismatch":
        state.write_text(
            json.dumps(
                {
                    "token": "0" * 64,
                    "completed": checkpoint.completed,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(
        webvpn.run_batches(batches, execute, checkpoint=checkpoint)
    )

    assert seen == [1]
    assert summary["batches_completed"] == 1


def test_checkpoint_replace_failure_never_restores_sensitive_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [_record(batches[0])],
                        "expression": batches[0].expression,
                        "result_url": "https://example.invalid/result",
                        "html": "<table>secret</table>",
                        "cookie": "ticket=secret",
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    checkpoint = webvpn.BatchCheckpoint(state)
    executor_calls: list[int] = []

    def fail_replace(_source, _destination) -> None:
        raise OSError("replace denied")

    monkeypatch.setattr(os, "replace", fail_replace)

    async def execute(batch):
        executor_calls.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=checkpoint,
            should_stop=lambda results: bool(results[0]["records"]),
        )
    )

    assert executor_calls == []
    assert checkpoint.completed == {}
    assert summary["complete"] is False
    assert summary["limit_reached"] is False
    assert summary["terminal_status"] == SearchStatus.CONFIGURATION_ERROR.value
    assert summary["results"] == []
    assert not list(tmp_path.glob(f".{state.name}.*.tmp"))


def test_checkpoint_save_failure_discards_already_restored_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [_record(batches[0])],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    checkpoint = webvpn.BatchCheckpoint(state)
    real_replace = os.replace
    replace_calls = 0

    def fail_second_replace(source, destination) -> None:
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 2:
            raise OSError("replace denied after restore")
        real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_second_replace)
    executor_calls: list[int] = []

    async def execute(batch):
        executor_calls.append(batch.index)
        return _challenge(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=checkpoint,
        )
    )

    assert executor_calls == [2]
    assert checkpoint.completed == {}
    assert summary["results"] == []
    assert summary["batches_completed"] == 0
    assert summary["limit_reached"] is False
    assert summary["terminal_status"] == SearchStatus.CONFIGURATION_ERROR.value
    assert not list(tmp_path.glob(f".{state.name}.*.tmp"))


@pytest.mark.parametrize(
    "saved_status",
    [
        "anything",
        SearchStatus.CHALLENGE_DETECTED.value,
        SearchStatus.CONFIGURATION_ERROR.value,
    ],
)
def test_checkpoint_rejects_non_completed_statuses(
    tmp_path: Path,
    saved_status: str,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": saved_status,
                        "index": 1,
                        "records": [],
                        "incomplete_records": [],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


def test_checkpoint_rejects_no_results_with_records(tmp_path: Path) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.NO_RESULTS.value,
                        "index": 1,
                        "records": [_record(batches[0])],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


@pytest.mark.parametrize(
    ("title", "year"),
    [
        ("畸形年度", 1800),
        ("", 2025),
    ],
    ids=["unverifiable_year", "missing_title"],
)
def test_checkpoint_rejects_malformed_formal_records(
    tmp_path: Path,
    title: str,
    year: int,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0], title=title)
    record["publication_year"] = year
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


def test_checkpoint_whitelist_drops_sensitive_auxiliary_fields(
    tmp_path: Path,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0])
    record.update(
        {
            "search_query": batches[0].expression,
            "detail": "https://example.invalid/<table>cookie",
            "warnings": ["C:\\Users\\example\\profile"],
        }
    )
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                        "detail": batches[0].expression,
                        "warnings": ["https://example.invalid"],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    async def execute(batch):
        return _challenge(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    text = state.read_text(encoding="utf-8")
    for forbidden in (
        "search_query",
        "detail",
        "warnings",
        "SU %=",
        "https://",
        "<table",
        "cookie",
        "C:\\Users",
    ):
        assert forbidden.casefold() not in text.casefold()


def test_checkpoint_rejects_sensitive_text_hidden_in_allowed_record_field(
    tmp_path: Path,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0])
    record["source_database"] = "https://example.invalid/<table>cookie"
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


def test_checkpoint_read_error_fails_closed_without_network_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = tmp_path / "progress.json"
    state.write_text("{}", encoding="utf-8")
    batches = _batches(1)
    executor_calls: list[int] = []
    original_read_text = Path.read_text

    def fail_state_read(path: Path, *args, **kwargs):
        if path == state:
            raise OSError("read denied")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_state_read)

    async def execute(batch):
        executor_calls.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert executor_calls == []
    assert summary["results"] == []
    assert summary["batches_completed"] == 0
    assert summary["limit_reached"] is False
    assert summary["terminal_status"] == SearchStatus.CONFIGURATION_ERROR.value


def test_checkpoint_clear_error_fails_closed_instead_of_leaking_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    executor_calls: list[int] = []
    original_unlink = Path.unlink

    def fail_state_unlink(path: Path, *args, **kwargs):
        if path == state:
            raise OSError("unlink denied")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_state_unlink)

    async def execute(batch):
        executor_calls.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert executor_calls == [1]
    assert summary["results"] == []
    assert summary["batches_completed"] == 0
    assert summary["limit_reached"] is False
    assert summary["terminal_status"] == SearchStatus.CONFIGURATION_ERROR.value


@pytest.mark.parametrize("field", ["title", "journal_raw"])
def test_checkpoint_rejects_formal_record_blank_after_control_cleanup(
    tmp_path: Path,
    field: str,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0])
    record[field] = "\u200b\x00"
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


@pytest.mark.parametrize(
    ("total_rows", "excluded", "records", "incomplete"),
    [
        (True, 0, [], []),
        (0, True, [], []),
        (-1, 0, [], []),
        (1, 2, [], []),
        (1, 0, ["formal"], ["incomplete"]),
    ],
    ids=[
        "bool_total",
        "bool_excluded",
        "negative_total",
        "excluded_gt_total",
        "row_count_underflow",
    ],
)
def test_checkpoint_rejects_inconsistent_count_semantics(
    tmp_path: Path,
    total_rows,
    excluded,
    records,
    incomplete,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    formal = _record(batches[0])
    incomplete_record = _record(batches[0], title="")
    payload_records = [formal] if records else []
    payload_incomplete = [incomplete_record] if incomplete else []
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": total_rows,
                        "excluded_non_journal_rows": excluded,
                        "records": payload_records,
                        "incomplete_records": payload_incomplete,
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("document_type", "报纸"),
        ("source_database", "Crossref"),
        ("citations", -1),
        ("downloads", -1),
        ("result_rank", -1),
    ],
)
def test_checkpoint_rejects_values_outside_record_field_contract(
    tmp_path: Path,
    field: str,
    value,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0])
    record[field] = value
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


def test_checkpoint_count_lower_bound_allows_formal_rows_omitted_by_limit(
    tmp_path: Path,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 8,
                        "excluded_non_journal_rows": 2,
                        "records": [_record(batches[0])],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _challenge(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [2]
    assert summary["results"][0]["total_rows"] == 8
    assert len(summary["results"][0]["records"]) == 1


def test_checkpoint_rejects_formal_record_hidden_in_incomplete_records(
    tmp_path: Path,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [],
                        "incomplete_records": [_record(batches[0])],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


@pytest.mark.parametrize(
    "unsafe_date",
    [
        "  Ｃ：＼Users＼secret  ",
        "  ＼＼server＼share  ",
        "  ／etc/passwd  ",
        "  ～／secret  ",
        "  ｈｔｔｐｓ：／／example.invalid  ",
        "\u200bＣ：＼Users＼secret",
        "ｈｔ\u200bｔｐｓ：／／example.invalid",
    ],
    ids=[
        "windows_drive",
        "unc",
        "posix_absolute",
        "home",
        "url",
        "zero_width_windows_drive",
        "zero_width_url",
    ],
)
def test_checkpoint_path_checks_normalize_nfkc_and_trim_first(
    tmp_path: Path,
    unsafe_date: str,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0])
    record["publication_date"] = unsafe_date
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


@pytest.mark.parametrize(
    "unsafe_date",
    [
        "\\Windows\\System32\\config",
        "\\Device\\HarddiskVolume1\\secret",
        "\\??\\C:\\secret",
        "  FiLe:/C:/secret  ",
        "FILE://server/share",
        "file:C:/secret",
        "  ｆｉｌｅ：／Ｃ：／secret  ",
        "  ｆ ｉ ｌ ｅ ： ／Ｃ：／secret  ",
    ],
    ids=[
        "windows_root",
        "nt_device",
        "nt_namespace",
        "file_single_slash_mixed_case_space",
        "file_double_slash",
        "file_no_slash",
        "file_fullwidth",
        "file_internal_space_fullwidth",
    ],
)
def test_checkpoint_rejects_windows_namespace_and_file_uri_variants(
    tmp_path: Path,
    unsafe_date: str,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0])
    record["publication_date"] = unsafe_date
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]


@pytest.mark.parametrize(
    "title",
    [
        "路径符号 A\\B 的规范用法",
        "File handling in empirical research",
        "File: an empirical methods note",
    ],
)
def test_checkpoint_allows_internal_backslash_and_ordinary_file_word(
    tmp_path: Path,
    title: str,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0], title=title)
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    async def execute(batch):
        return _challenge(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert summary["results"][0]["records"][0].title == title


def test_checkpoint_preserves_normal_title_slash_and_saves_normalized_text(
    tmp_path: Path,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(2)
    token = webvpn._checkpoint_token(batches)
    record = _record(batches[0], title="Ａ投入／产出分析")
    state.write_text(
        json.dumps(
            {
                "token": token,
                "completed": {
                    "1": {
                        "status": SearchStatus.SUCCESS.value,
                        "index": 1,
                        "total_rows": 1,
                        "excluded_non_journal_rows": 0,
                        "records": [record],
                        "incomplete_records": [],
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    async def execute(batch):
        return _challenge(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert summary["results"][0]["records"][0].title == "A投入/产出分析"
    text = state.read_text(encoding="utf-8")
    assert "A投入/产出分析" in text
    assert "Ａ投入／产出分析" not in text


@pytest.mark.parametrize(
    "malformed_completed",
    [
        None,
        {"1": {"status": SearchStatus.SUCCESS.value, "records": None}},
        {"1": {"status": SearchStatus.SUCCESS.value, "records": [7]}},
        {
            "1": {
                "status": SearchStatus.SUCCESS.value,
                "records": [
                    {
                        "title": "畸形作者题录",
                        "authors": "张三",
                        "journal_raw": "管理世界",
                        "publication_date": "2025-03-11",
                        "publication_year": 2025,
                        "document_type": "期刊",
                        "citations": None,
                        "downloads": None,
                        "is_online_first": False,
                        "result_rank": 1,
                        "source_database": "CNKI",
                    }
                ],
            }
        },
    ],
    ids=[
        "completed_not_dict",
        "records_null",
        "record_not_dict",
        "authors_string",
    ],
)
def test_malformed_checkpoint_entries_are_discarded_without_crashing(
    tmp_path: Path,
    malformed_completed,
) -> None:
    state = tmp_path / "progress.json"
    batches = _batches(1)
    token = webvpn._checkpoint_token(batches)
    state.write_text(
        json.dumps(
            {"token": token, "completed": malformed_completed},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    seen: list[int] = []

    async def execute(batch):
        seen.append(batch.index)
        return _ok(batch)

    summary = asyncio.run(
        webvpn.run_batches(
            batches,
            execute,
            checkpoint=webvpn.BatchCheckpoint(state),
        )
    )

    assert seen == [1]
    assert summary["complete"] is True
    assert summary["terminal_status"] is None


def test_checkpoint_is_cleared_after_a_complete_run(tmp_path: Path) -> None:
    state = tmp_path / "progress.json"
    checkpoint = webvpn.BatchCheckpoint(state)

    async def execute(batch):
        return _ok(batch)

    asyncio.run(webvpn.run_batches(_batches(2), execute, checkpoint=checkpoint))
    assert not state.exists()


# ── 节流 ────────────────────────────────────────────────────────────────────

def test_throttle_waits_only_when_the_interval_has_not_elapsed(tmp_path: Path) -> None:
    clock = [1000.0]
    slept: list[float] = []

    async def sleep(delay: float) -> None:
        slept.append(delay)
        clock[0] += delay

    throttle = webvpn.Throttle(tmp_path / "throttle", min_interval=30.0,
                               sleep=sleep, now=lambda: clock[0])

    assert asyncio.run(throttle.wait()) == 0.0        # 无历史记录，不等待
    throttle.record()
    clock[0] += 10
    assert asyncio.run(throttle.wait()) == pytest.approx(20.0)
    clock[0] += 100
    assert asyncio.run(throttle.wait()) == 0.0
    assert slept == [pytest.approx(20.0)]


def test_challenge_adds_extra_backoff_on_top_of_the_interval(tmp_path: Path) -> None:
    clock = [1000.0]

    async def sleep(delay: float) -> None:
        clock[0] += delay

    throttle = webvpn.Throttle(tmp_path / "throttle", min_interval=30.0,
                               challenge_backoff=180.0, sleep=sleep, now=lambda: clock[0])
    throttle.record(challenged=True)
    assert asyncio.run(throttle.wait()) == pytest.approx(210.0)


def test_throttle_state_survives_a_fresh_instance(tmp_path: Path) -> None:
    """常驻模式下模块可能被重载，只有落盘的状态才活得过重载。"""
    state = tmp_path / "throttle"
    clock = [500.0]

    async def sleep(delay: float) -> None:
        clock[0] += delay

    webvpn.Throttle(state, now=lambda: clock[0], sleep=sleep).record()
    reloaded = webvpn.Throttle(state, min_interval=30.0, now=lambda: clock[0], sleep=sleep)
    assert asyncio.run(reloaded.wait()) == pytest.approx(30.0)


def test_run_batches_applies_throttle_between_batches(tmp_path: Path) -> None:
    clock = [0.0]

    async def sleep(delay: float) -> None:
        clock[0] += delay

    throttle = webvpn.Throttle(tmp_path / "throttle", min_interval=30.0,
                               sleep=sleep, now=lambda: clock[0])

    async def execute(batch):
        clock[0] += 1
        return _ok(batch)

    asyncio.run(webvpn.run_batches(_batches(3), execute, throttle=throttle))
    assert clock[0] >= 60.0        # 3 批之间至少等待两个完整间隔


# ── 会话生命周期 ────────────────────────────────────────────────────────────

class FakePage:
    def __init__(self, titles: list[str]) -> None:
        self.titles = titles
        self.closed = False
        self.visited: list[str] = []

    async def goto(self, url: str, *, wait_until: str) -> None:
        self.visited.append(url)

    async def title(self) -> str:
        return self.titles.pop(0) if len(self.titles) > 1 else self.titles[0]

    async def close(self) -> None:
        self.closed = True

    def is_closed(self) -> bool:
        return self.closed


class FakeContext:
    def __init__(self, page: FakePage) -> None:
        self.pages = [page]
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeBrowser:
    def __init__(self, context: FakeContext) -> None:
        self.context = context
        self.closed = False
        self.new_context_calls: list[dict] = []

    async def new_context(self, **kwargs) -> FakeContext:
        self.new_context_calls.append(kwargs)
        return self.context

    async def close(self) -> None:
        self.closed = True


class FakeChromium:
    def __init__(self, browser: FakeBrowser) -> None:
        self.browser = browser
        self.launch_calls: list[dict] = []

    async def launch(self, **kwargs) -> FakeBrowser:
        self.launch_calls.append(kwargs)
        return self.browser


class FakePlaywright:
    def __init__(self, browser: FakeBrowser) -> None:
        self.chromium = FakeChromium(browser)
        self.stopped = False

    async def stop(self) -> None:
        self.stopped = True


class FakeFactory:
    def __init__(self, playwright: FakePlaywright) -> None:
        self.playwright = playwright
        self.launch_calls = 0

    async def launch(self):
        self.launch_calls += 1
        return await webvpn._EphemeralContextFactory(self.playwright).launch()


def _session(titles: list[str]):
    page = FakePage(titles)
    context = FakeContext(page)
    browser = FakeBrowser(context)
    playwright = FakePlaywright(browser)
    factory = FakeFactory(playwright)
    config = webvpn.WebVpnConfig("https://webvpn.example.edu.cn/https/abc/",
                                 login_timeout_seconds=30, poll_interval_seconds=1)
    session = webvpn.WebVpnSession(config, context_factory=factory)
    return session, page, context, browser, playwright, factory


def test_session_waits_until_the_signed_in_home_page_appears() -> None:
    session, page, context, _browser, _playwright, _factory = _session(
        ["统一身份认证平台", "统一身份认证平台", "中国知网"])

    async def scenario() -> None:
        async with session:
            await session.wait_until_ready(sleep=_instant, now=_counter())

    asyncio.run(scenario())
    assert page.visited == ["https://webvpn.example.edu.cn/https/abc/"]
    assert context.closed


def test_session_times_out_when_login_never_completes() -> None:
    session, _page, _context, _browser, _playwright, _factory = _session(
        ["统一身份认证平台"])

    async def scenario() -> None:
        async with session:
            await session.wait_until_ready(sleep=_instant, now=_counter(step=10))

    with pytest.raises(webvpn.WebVpnLoginTimeout):
        asyncio.run(scenario())


def test_closing_the_window_is_reported_as_a_dedicated_error() -> None:
    """关窗等同于登出，必须给出可行动的提示而不是崩溃。"""
    session, page, _context, _browser, _playwright, _factory = _session(["中国知网"])

    async def scenario() -> None:
        async with session:
            session.ensure_open()
            page.closed = True
            session.ensure_open()

    with pytest.raises(webvpn.WebVpnWindowClosed):
        asyncio.run(scenario())


def test_session_uses_ephemeral_context_and_closes_every_resource() -> None:
    session, _page, context, browser, playwright, factory = _session(["中国知网"])

    async def scenario() -> None:
        async with session:
            assert factory.launch_calls == 1
            assert playwright.chromium.launch_calls == [{"headless": False}]
            assert browser.new_context_calls == [{
                "locale": "zh-CN",
                "accept_downloads": False,
            }]
        assert context.closed
        assert browser.closed
        assert playwright.stopped
        await session.close()

    asyncio.run(scenario())


def test_ephemeral_factory_closes_browser_when_context_creation_fails() -> None:
    page = FakePage(["中国知网"])
    context = FakeContext(page)
    browser = FakeBrowser(context)
    playwright = FakePlaywright(browser)
    failure = RuntimeError("new_context failed")

    async def fail_new_context(**_kwargs):
        raise failure

    browser.new_context = fail_new_context

    async def scenario() -> None:
        with pytest.raises(webvpn.BrowserUnavailableError) as raised:
            await webvpn._EphemeralContextFactory(playwright).launch()
        assert raised.value.__cause__ is failure

    asyncio.run(scenario())
    assert browser.closed


def test_ephemeral_factory_closes_browser_when_context_creation_is_cancelled() -> None:
    page = FakePage(["中国知网"])
    context = FakeContext(page)
    browser = FakeBrowser(context)
    playwright = FakePlaywright(browser)
    cancellation = asyncio.CancelledError("new_context cancelled")

    async def cancel_new_context(**_kwargs):
        raise cancellation

    browser.new_context = cancel_new_context

    async def scenario() -> None:
        with pytest.raises(asyncio.CancelledError) as raised:
            await webvpn._EphemeralContextFactory(playwright).launch()
        assert raised.value is cancellation

    asyncio.run(scenario())
    assert browser.closed


def test_session_cleans_up_when_factory_launch_fails_and_preserves_error() -> None:
    page = FakePage(["中国知网"])
    context = FakeContext(page)
    browser = FakeBrowser(context)
    playwright = FakePlaywright(browser)
    failure = RuntimeError("launch failed")

    class LaunchFailFactory:
        async def launch(self):
            raise failure

    factory = LaunchFailFactory()
    factory.playwright = playwright
    session = webvpn.WebVpnSession(
        webvpn.WebVpnConfig("https://webvpn.example.edu.cn/https/abc/"),
        context_factory=factory,
    )

    async def scenario() -> None:
        with pytest.raises(RuntimeError) as raised:
            await session.__aenter__()
        assert raised.value is failure

    asyncio.run(scenario())
    assert playwright.stopped


@pytest.mark.parametrize(
    "initial_failure",
    [RuntimeError("goto failed"), asyncio.CancelledError("goto cancelled")],
    ids=["original_error", "original_cancellation"],
)
def test_session_finishes_cleanup_when_enter_task_is_cancelled_again(
    initial_failure: BaseException,
) -> None:
    session, page, context, browser, playwright, _factory = _session(["中国知网"])
    cleanup_started = asyncio.Event()
    allow_cleanup = asyncio.Event()

    async def fail_goto(_url: str, *, wait_until: str):
        raise initial_failure

    async def slow_context_close() -> None:
        cleanup_started.set()
        await allow_cleanup.wait()
        context.closed = True

    page.goto = fail_goto
    context.close = slow_context_close

    async def scenario() -> BaseException:
        async def enter() -> BaseException:
            try:
                await session.__aenter__()
            except BaseException as raised:
                return raised
            raise AssertionError("__aenter__ 应当失败")

        task = asyncio.create_task(enter())
        await cleanup_started.wait()
        task.cancel()
        await asyncio.sleep(0)
        task.cancel()
        await asyncio.sleep(0)
        allow_cleanup.set()
        result = await task
        for _ in range(5):
            await asyncio.sleep(0)
        return result

    raised = asyncio.run(scenario())

    assert raised is initial_failure
    assert context.closed
    assert browser.closed
    assert playwright.stopped


def test_session_cleans_up_when_new_page_fails_and_preserves_error() -> None:
    page = FakePage(["中国知网"])
    context = FakeContext(page)
    context.pages = []
    browser = FakeBrowser(context)
    playwright = FakePlaywright(browser)
    factory = FakeFactory(playwright)
    failure = RuntimeError("new_page failed")

    async def fail_new_page():
        raise failure

    context.new_page = fail_new_page
    session = webvpn.WebVpnSession(
        webvpn.WebVpnConfig("https://webvpn.example.edu.cn/https/abc/"),
        context_factory=factory,
    )

    async def scenario() -> None:
        with pytest.raises(RuntimeError) as raised:
            await session.__aenter__()
        assert raised.value is failure

    asyncio.run(scenario())
    assert context.closed
    assert browser.closed
    assert playwright.stopped


def test_session_cleans_up_when_home_navigation_fails_and_preserves_error() -> None:
    session, page, context, browser, playwright, _factory = _session(["中国知网"])
    failure = RuntimeError("goto failed")

    async def fail_goto(_url: str, *, wait_until: str):
        raise failure

    page.goto = fail_goto

    async def scenario() -> None:
        with pytest.raises(RuntimeError) as raised:
            await session.__aenter__()
        assert raised.value is failure

    asyncio.run(scenario())
    assert context.closed
    assert browser.closed
    assert playwright.stopped


async def _instant(_delay: float) -> None:
    return None


def _counter(step: float = 1.0):
    ticks = [0.0]

    def now() -> float:
        ticks[0] += step
        return ticks[0]

    return now
