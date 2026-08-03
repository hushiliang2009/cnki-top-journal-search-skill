import asyncio

import pytest

from cnki_search import professional_runtime
from cnki_search.professional import PlanExecutionResult


class FakeSession:
    def __init__(self) -> None:
        self.ensure_open_calls = 0
        self.close_calls = 0

    def ensure_open(self) -> None:
        self.ensure_open_calls += 1

    async def close(self) -> None:
        self.close_calls += 1


def test_runtime_serializes_calls_and_cancelled_queue_never_enters_service() -> None:
    from cnki_search.professional_runtime import ProfessionalSearchRuntime

    async def scenario() -> None:
        first_entered = asyncio.Event()
        release_first = asyncio.Event()

        class Service:
            def __init__(self) -> None:
                self.calls: list[str] = []

            async def search_group(
                self, topic, group, *, limit, year_from, year_to
            ):
                self.calls.append(topic)
                first_entered.set()
                await release_first.wait()
                return {"status": "success"}

        session = FakeSession()
        service = Service()
        runtime = ProfessionalSearchRuntime(session, service)
        first = asyncio.create_task(
            runtime.search_group(
                "先进入", "cssci", limit=50, year_from=None, year_to=None
            )
        )
        await first_entered.wait()
        queued = asyncio.create_task(
            runtime.search_group(
                "排队后取消", "cssci", limit=50, year_from=None, year_to=None
            )
        )
        await asyncio.sleep(0)
        queued.cancel()
        with pytest.raises(asyncio.CancelledError):
            await queued
        release_first.set()
        assert await first == {"status": "success"}
        assert service.calls == ["先进入"]
        assert session.ensure_open_calls == 1

    asyncio.run(scenario())


def test_runtime_aclose_closes_session_once_and_rejects_new_calls() -> None:
    from cnki_search.professional_runtime import ProfessionalSearchRuntime

    async def scenario() -> None:
        class Service:
            async def search_group(self, *_args, **_kwargs):
                raise AssertionError("关闭后不得进入服务")

        session = FakeSession()
        runtime = ProfessionalSearchRuntime(session, Service())
        await runtime.aclose()
        await runtime.aclose()
        assert session.close_calls == 1
        with pytest.raises(RuntimeError, match="运行时已关闭"):
            await runtime.search_group(
                "主题", "cssci", limit=50, year_from=None, year_to=None
            )

    asyncio.run(scenario())


def test_batch_executor_opens_from_home_and_closes_only_result_tab(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cnki_search.professional import ExpressionBatch

    async def scenario() -> None:
        events: list[str] = []

        class Page:
            def __init__(self, name: str) -> None:
                self.name = name
                self.closed = False

            async def close(self) -> None:
                self.closed = True
                events.append(f"close:{self.name}")

        home = Page("home")
        result = Page("result")
        session = type(
            "Session",
            (),
            {
                "page": home,
                "context": object(),
                "ensure_open": lambda self: None,
            },
        )()

        class Driver:
            def __init__(self, page) -> None:
                assert page is home
                self.page = page

            async def open_from_home(self, context, *, preserve_home=False):
                assert context is session.context
                assert preserve_home is True
                events.append("open")
                self.page = result
                return result

            async def switch_to_professional(self):
                events.append("switch")

            async def execute_plan(self, plan):
                events.append(f"execute:{plan.expression}")
                return "success", "<html>ok</html>", "https://secret/result"

        monkeypatch.setattr(professional_runtime, "ProfessionalSearchPage", Driver)
        executor = professional_runtime.ProfessionalBatchExecutor(session)
        plan = ExpressionBatch(1, 1, (), "SU %= '数字经济'")

        assert await executor(plan) == PlanExecutionResult("success", "<html>ok</html>", "")
        assert events == [
            "open",
            "switch",
            "execute:SU %= '数字经济'",
            "close:result",
        ]
        assert home.closed is False
        assert result.closed is True

    asyncio.run(scenario())


def test_challenge_page_is_only_observed_then_closed_before_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cnki_search import professional_runtime
    from cnki_search.professional import ExpressionBatch
    from cnki_search.webvpn import CAPTCHA_VIEWPORT_JS

    async def scenario() -> None:
        class ChallengePage:
            def __init__(self) -> None:
                self.visible = [True, False]
                self.closed = False
                self.evaluations: list[tuple[object, object]] = []

            async def evaluate(self, script, markers):
                self.evaluations.append((script, markers))
                return self.visible.pop(0)

            async def close(self) -> None:
                self.closed = True

            def is_closed(self) -> bool:
                return self.closed

        home = object()
        challenge = ChallengePage()
        session = type(
            "Session",
            (),
            {
                "page": home,
                "context": object(),
                "ensure_open": lambda self: None,
            },
        )()

        class Driver:
            def __init__(self, page) -> None:
                self.page = page

            async def open_from_home(self, _context, *, preserve_home=False):
                assert preserve_home is True
                self.page = challenge
                return challenge

            async def switch_to_professional(self):
                return None

            async def execute_plan(self, _plan):
                return "challenge_detected", "", "https://secret/challenge"

        async def no_sleep(_delay: float) -> None:
            return None

        monkeypatch.setattr(professional_runtime, "ProfessionalSearchPage", Driver)
        executor = professional_runtime.ProfessionalBatchExecutor(
            session, sleep=no_sleep, challenge_poll_seconds=0
        )
        plan = ExpressionBatch(1, 1, (), "SU %= '数字经济'")

        assert await executor(plan) == PlanExecutionResult("challenge_detected", "", "")
        assert challenge.closed is False
        assert executor.active_challenge_page is challenge
        assert await executor.wait_for_manual_challenge(plan) is True
        assert challenge.closed is True
        assert executor.active_challenge_page is None
        assert [item[0] for item in challenge.evaluations] == [
            CAPTCHA_VIEWPORT_JS,
            CAPTCHA_VIEWPORT_JS,
        ]

    asyncio.run(scenario())


def test_challenge_wait_never_exceeds_the_600_second_limit() -> None:
    from cnki_search.professional import ExpressionBatch
    from cnki_search.professional_runtime import ProfessionalBatchExecutor

    async def scenario() -> None:
        elapsed = [0.0]

        class ChallengePage:
            def __init__(self) -> None:
                self.closed = False

            async def evaluate(self, _script, _markers):
                return True

            async def close(self) -> None:
                self.closed = True

            def is_closed(self) -> bool:
                return self.closed

        async def advance(delay: float) -> None:
            elapsed[0] += delay

        session = type("Session", (), {})()
        page = ChallengePage()
        executor = ProfessionalBatchExecutor(
            session,
            sleep=advance,
            now=lambda: elapsed[0],
        )
        executor.active_challenge_page = page
        plan = ExpressionBatch(1, 1, (), "SU %= '数字经济'")

        assert await executor.wait_for_manual_challenge(plan) is False
        assert elapsed[0] == 600.0
        assert page.closed is True

    asyncio.run(scenario())


def test_challenge_wait_has_a_hard_limit_when_evaluate_is_slow() -> None:
    from time import monotonic

    from cnki_search.professional import ExpressionBatch
    from cnki_search.professional_runtime import ProfessionalBatchExecutor

    async def scenario() -> None:
        class SlowPage:
            def __init__(self) -> None:
                self.closed = False

            async def evaluate(self, _script, _markers):
                await asyncio.sleep(0.2)
                return True

            async def close(self) -> None:
                self.closed = True

            def is_closed(self) -> bool:
                return self.closed

        page = SlowPage()
        # 本用例断言"观察被硬性打断，且页面仍被关闭"，因此清理预算必须真的够用。
        # 清理预算是 challenge_timeout_seconds / 2：取 0.03 时只有约 15 毫秒，
        # 已低于 Windows 事件循环定时器约 15.6 毫秒的粒度，关闭协程可能来不及
        # 被调度就超时，测试随机变红（Windows CI 三次里失败两次）。
        # 取 0.3 使预算变为 150 毫秒，远高于时钟粒度；同时观察窗口 150 毫秒仍
        # 小于 evaluate 的 200 毫秒，硬性打断这一被测性质不受影响。
        executor = ProfessionalBatchExecutor(
            type("Session", (), {})(),
            challenge_timeout_seconds=0.3,
            challenge_poll_seconds=0,
        )
        executor.active_challenge_page = page
        started = monotonic()
        result = await executor.wait_for_manual_challenge(
            ExpressionBatch(1, 1, (), "SU %= '数字经济'")
        )
        elapsed = monotonic() - started

        assert result is False
        assert elapsed < 0.5
        assert page.closed is True

    asyncio.run(scenario())


def test_challenge_wait_has_a_hard_limit_when_evaluate_never_returns() -> None:
    from cnki_search.professional import ExpressionBatch
    from cnki_search.professional_runtime import ProfessionalBatchExecutor

    async def scenario() -> None:
        class HangingPage:
            def __init__(self) -> None:
                self.closed = False

            async def evaluate(self, _script, _markers):
                await asyncio.Event().wait()

            async def close(self) -> None:
                self.closed = True

            def is_closed(self) -> bool:
                return self.closed

        page = HangingPage()
        executor = ProfessionalBatchExecutor(
            type("Session", (), {})(),
            # 给 Windows 全量回归的调度留出关闭窗口；上一个慢速求值测试仍以
            # 0.03 秒预算区分旧实现的 0.2 秒等待。
            challenge_timeout_seconds=0.2,
            challenge_poll_seconds=0,
        )
        executor.active_challenge_page = page
        plan = ExpressionBatch(1, 1, (), "SU %= '数字经济'")

        assert await asyncio.wait_for(
            executor.wait_for_manual_challenge(plan), timeout=0.5
        ) is False
        assert page.closed is True

    asyncio.run(scenario())


def test_challenge_wait_includes_slow_page_close_in_hard_limit() -> None:
    from time import monotonic

    from cnki_search.professional import ExpressionBatch
    from cnki_search.professional_runtime import ProfessionalBatchExecutor

    async def scenario() -> None:
        class SlowClosePage:
            async def evaluate(self, _script, _markers):
                return False

            async def close(self) -> None:
                await asyncio.sleep(0.2)

            def is_closed(self) -> bool:
                return False

        executor = ProfessionalBatchExecutor(
            type("Session", (), {})(),
            challenge_timeout_seconds=0.03,
            challenge_poll_seconds=0,
        )
        executor.active_challenge_page = SlowClosePage()
        started = monotonic()
        result = await executor.wait_for_manual_challenge(
            ExpressionBatch(1, 1, (), "SU %= '数字经济'")
        )
        elapsed = monotonic() - started

        assert result is False
        assert elapsed < 0.12

    asyncio.run(scenario())


def test_cancellation_during_challenge_close_is_propagated_after_cleanup() -> None:
    from cnki_search.professional import ExpressionBatch
    from cnki_search.professional_runtime import ProfessionalBatchExecutor

    async def scenario() -> None:
        close_started = asyncio.Event()

        class Page:
            def __init__(self) -> None:
                self.closed = False

            async def evaluate(self, _script, _markers):
                return False

            async def close(self) -> None:
                close_started.set()
                await asyncio.sleep(0.02)
                self.closed = True

            def is_closed(self) -> bool:
                return self.closed

        page = Page()
        executor = ProfessionalBatchExecutor(
            type("Session", (), {})(),
            challenge_timeout_seconds=0.2,
            challenge_poll_seconds=0,
        )
        executor.active_challenge_page = page
        task = asyncio.create_task(
            executor.wait_for_manual_challenge(
                ExpressionBatch(1, 1, (), "SU %= '数字经济'")
            )
        )
        await close_started.wait()
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task
        assert page.closed is True

    asyncio.run(scenario())


def test_challenge_close_and_client_cancel_same_turn_still_propagates() -> None:
    from cnki_search.professional import ExpressionBatch
    from cnki_search.professional_runtime import ProfessionalBatchExecutor

    async def scenario() -> None:
        close_started = asyncio.Event()
        release_close = asyncio.Event()

        class Page:
            def __init__(self) -> None:
                self.closed = False

            async def evaluate(self, _script, _markers):
                return False

            async def close(self) -> None:
                close_started.set()
                await release_close.wait()
                self.closed = True

            def is_closed(self) -> bool:
                return self.closed

        page = Page()
        executor = ProfessionalBatchExecutor(
            type("Session", (), {})(),
            challenge_timeout_seconds=0.2,
            challenge_poll_seconds=0,
        )
        executor.active_challenge_page = page
        task = asyncio.create_task(
            executor.wait_for_manual_challenge(
                ExpressionBatch(1, 1, (), "SU %= '数字经济'")
            )
        )
        await close_started.wait()
        loop = asyncio.get_running_loop()
        loop.call_soon(release_close.set)
        loop.call_soon(task.cancel)

        with pytest.raises(asyncio.CancelledError):
            await task
        assert page.closed is True

    asyncio.run(scenario())


def test_environment_factory_requires_home_before_constructing_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cnki_search import professional_runtime

    monkeypatch.delenv("CNKI_WEBVPN_HOME", raising=False)

    class ForbiddenSession:
        def __init__(self, _config) -> None:
            raise AssertionError("缺少配置时不得启动浏览器")

    monkeypatch.setattr(professional_runtime, "WebVpnSession", ForbiddenSession)
    with pytest.raises(ValueError, match="请设置 CNKI_WEBVPN_HOME"):
        asyncio.run(professional_runtime.build_professional_runtime_from_env())


def test_environment_factory_closes_session_when_initialization_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cnki_search import professional_runtime

    session = None

    class FailingSession:
        def __init__(self, config) -> None:
            nonlocal session
            self.config = config
            self.close_calls = 0
            session = self

        async def __aenter__(self):
            return self

        async def wait_until_ready(self) -> None:
            raise RuntimeError("登录初始化失败")

        async def close(self) -> None:
            self.close_calls += 1

    monkeypatch.setenv(
        "CNKI_WEBVPN_HOME", "https://webvpn.example.edu.cn/https/abc/"
    )
    monkeypatch.setattr(professional_runtime, "WebVpnSession", FailingSession)

    with pytest.raises(RuntimeError, match="登录初始化失败"):
        asyncio.run(professional_runtime.build_professional_runtime_from_env())
    assert session is not None
    assert session.close_calls == 1


def test_environment_factory_closes_session_when_initialization_is_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cnki_search import professional_runtime

    session = None

    class WaitingSession:
        def __init__(self, config) -> None:
            nonlocal session
            self.config = config
            self.started = asyncio.Event()
            self.close_calls = 0
            session = self

        async def __aenter__(self):
            return self

        async def wait_until_ready(self) -> None:
            self.started.set()
            await asyncio.Event().wait()

        async def close(self) -> None:
            self.close_calls += 1

    monkeypatch.setenv(
        "CNKI_WEBVPN_HOME", "https://webvpn.example.edu.cn/https/abc/"
    )
    monkeypatch.setattr(professional_runtime, "WebVpnSession", WaitingSession)

    async def scenario() -> None:
        task = asyncio.create_task(
            professional_runtime.build_professional_runtime_from_env()
        )
        while session is None:
            await asyncio.sleep(0)
        await session.started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())
    assert session is not None
    assert session.close_calls == 1
