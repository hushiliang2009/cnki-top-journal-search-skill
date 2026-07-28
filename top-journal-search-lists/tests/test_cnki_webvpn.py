import asyncio
from pathlib import Path

import pytest

from cnki_search import webvpn
from cnki_search.models import SearchStatus
from cnki_search.professional import build_batches, build_expression


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


async def _instant(_delay: float) -> None:
    return None


def _counter(step: float = 1.0):
    ticks = [0.0]

    def now() -> float:
        ticks[0] += step
        return ticks[0]

    return now
