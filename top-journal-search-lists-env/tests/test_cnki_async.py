import asyncio
import os
from pathlib import Path
import subprocess
import sys

import pytest

import cnki_search_env.service as service_module
from cnki_search_env.mcp_server import CnkiMcpServer
from cnki_search_env.models import SearchOutcome, SearchStatus
from cnki_search_env.rate_limit import SerialSearchGate
from cnki_search_env.service import CnkiPublicSearchService
from cnki_search_env.session import PublicCnkiSession


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "环境科学与工程学科顶尖期刊目录_v3.0.md"


def test_async_gate_serializes_actual_start_times_without_real_sleep() -> None:
    async def scenario() -> None:
        now = [0.0]
        starts: list[float] = []

        async def sleep(delay: float) -> None:
            now[0] += delay

        gate = SerialSearchGate(
            minimum_interval=6.0,
            clock=lambda: now[0],
            sleep=sleep,
        )
        starts.append(await gate.wait())
        starts.append(await gate.wait())
        assert starts == [0.0, 6.0]
        assert now[0] == 6.0

    asyncio.run(scenario())


class _AsyncClosable:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True

    async def stop(self) -> None:
        self.closed = True


def test_async_session_cancellation_closes_every_resource() -> None:
    async def scenario() -> None:
        page = _AsyncClosable()
        page.goto = _blocked  # type: ignore[attr-defined]
        context = _AsyncClosable()
        context.new_page = lambda: page  # type: ignore[attr-defined]
        browser = _AsyncClosable()
        browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]
        playwright = _AsyncClosable()

        class Factory:
            async def launch_ephemeral(self):
                return browser

        session = PublicCnkiSession(browser_factory=Factory())
        session._playwright = playwright
        task = asyncio.create_task(_enter_and_search(session))
        await asyncio.sleep(0)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert page.closed and context.closed and browser.closed and playwright.closed

    async def _blocked(*_args, **_kwargs):
        await asyncio.Event().wait()

    async def _enter_and_search(session: PublicCnkiSession) -> None:
        async with session:
            await session.search("topic")

    asyncio.run(scenario())


def test_async_service_timeout_returns_network_error_and_queue_cancellation_does_not_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # 本测试只检验网络会话超时与排队取消；目录校验耗时另有专门测试覆盖。
    monkeypatch.setattr(service_module, "validate_catalog", lambda _path: None)

    async def scenario() -> None:
        started = 0
        entered = asyncio.Event()

        class Session:
            async def __aenter__(self):
                nonlocal started
                started += 1
                entered.set()
                return self

            async def __aexit__(self, *_exc):
                return None

            async def search(self, _query):
                await asyncio.Event().wait()

        service = CnkiPublicSearchService(
            session_factory=Session,
            catalog=CATALOG,
            gate=SerialSearchGate(minimum_interval=0),
            # 0.1 秒曾在 CI 的 ubuntu (3.12) 上不稳定：这段预算要覆盖两次
            # asyncio.to_thread 往返（含线程池惰性创建）与调度抖动，只削减
            # 目录解析成本仍不够。放大到 2.0 秒是消除竞赛本身，而不是降低概率；
            # 用例判定的是"超时后返回 network_error"，与具体数值无关。
            # 通用版 PR #11 已如此修正，环境版此前未同步。
            search_timeout_seconds=2.0,
        )
        outcome = await service.search("topic")
        assert outcome.status is SearchStatus.NETWORK_ERROR
        assert started == 1

        entered.clear()
        first = asyncio.create_task(service.search("first"))
        await entered.wait()
        queued = asyncio.create_task(service.search("second"))
        await asyncio.sleep(0)
        queued.cancel()
        try:
            await queued
        except asyncio.CancelledError:
            pass
        first.cancel()
        try:
            await first
        except asyncio.CancelledError:
            pass
        assert started == 2

    asyncio.run(scenario())


def test_cancellation_during_rate_sleep_never_opens_browser_session() -> None:
    async def scenario() -> None:
        sleeping = asyncio.Event()
        entered = 0

        async def sleep(_delay: float) -> None:
            sleeping.set()
            await asyncio.Event().wait()

        class Session:
            async def __aenter__(self):
                nonlocal entered
                entered += 1
                return self
            async def __aexit__(self, *_exc):
                return None
            async def search(self, _query):
                raise AssertionError("must not execute")

        gate = SerialSearchGate(minimum_interval=6, clock=lambda: 0.0, sleep=sleep)
        await gate.wait()
        service = CnkiPublicSearchService(session_factory=Session, catalog=CATALOG, gate=gate)
        task = asyncio.create_task(service.search("topic"))
        await sleeping.wait()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert entered == 0

    asyncio.run(scenario())


def test_cancellation_during_session_search_closes_resources() -> None:
    async def scenario() -> None:
        search_started = asyncio.Event()
        page, context, browser, playwright = _AsyncClosable(), _AsyncClosable(), _AsyncClosable(), _AsyncClosable()
        page.goto = lambda *_args, **_kwargs: type("Response", (), {"status": 200})()
        page.url = "https://www.cnki.net/"
        page.content = lambda: "<html></html>"
        page.title = lambda: "CNKI"
        class Body:
            async def inner_text(self, **_kwargs):
                search_started.set()
                await asyncio.Event().wait()
        page.locator = lambda _selector: Body()
        context.new_page = lambda: page
        browser.new_context = lambda **_kwargs: context
        class Factory:
            async def launch_ephemeral(self): return browser
        session = PublicCnkiSession(Factory())
        session._playwright = playwright
        async def run_search() -> None:
            async with session:
                await session.search("topic")
        task = asyncio.create_task(run_search())
        await search_started.wait()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert all(item.closed for item in (page, context, browser, playwright))

    asyncio.run(scenario())


def test_mcp_awaits_async_service_and_shutdown_cancels_active_task() -> None:
    async def scenario() -> None:
        started = asyncio.Event()

        class Service:
            async def search(self, query: str, limit: int = 20) -> SearchOutcome:
                started.set()
                await asyncio.Event().wait()
                return SearchOutcome(SearchStatus.NO_RESULTS, query, [], [], 0, [], "now")

        server = CnkiMcpServer(service=Service())
        task = asyncio.create_task(server.cnki_search_env("topic"))
        await started.wait()
        server.shutdown()
        server.shutdown()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert server._shutdown is True

    asyncio.run(scenario())


def test_async_timeout_and_shutdown_behave_independently_in_both_layouts() -> None:
    program = """
import asyncio
from pathlib import Path
import os
from cnki_search_env.mcp_server import CnkiMcpServer
from cnki_search_env.models import SearchOutcome, SearchStatus
from cnki_search_env.rate_limit import SerialSearchGate
from cnki_search_env.service import CnkiPublicSearchService

async def main():
    entered = asyncio.Event()
    mcp_started = asyncio.Event()
    class Session:
        async def __aenter__(self): entered.set(); return self
        async def __aexit__(self, *_exc): return None
        async def search(self, _query): await asyncio.Event().wait()
    catalog = Path(os.environ['CNKI_TEST_CATALOG'])
    service = CnkiPublicSearchService(session_factory=Session, catalog=catalog, gate=SerialSearchGate(minimum_interval=0), search_timeout_seconds=.01)
    assert (await service.search('topic')).status is SearchStatus.NETWORK_ERROR
    class Blocking:
        async def search(self, query, limit=20):
            mcp_started.set(); await asyncio.Event().wait()
    server = CnkiMcpServer(Blocking())
    task = asyncio.create_task(server.cnki_search_env('topic'))
    await mcp_started.wait(); server.shutdown(); server.shutdown()
    try: await task
    except asyncio.CancelledError: pass
    else: raise AssertionError('MCP task was not cancelled')
asyncio.run(main())
"""
    for root in (ROOT / "scripts", ROOT / "mcpb" / "src"):
        completed = subprocess.run(
            [sys.executable, "-c", program], cwd=root,
            env=os.environ | {"PYTHONPATH": str(root), "CNKI_TEST_CATALOG": str(CATALOG)}, capture_output=True, text=True,
        )
        assert completed.returncode == 0, completed.stderr


def test_entry_timeout_covers_slow_catalog_and_cache_in_both_layouts() -> None:
    program = """
import asyncio
import time
from pathlib import Path
import os
import cnki_search_env.service as service_module
from cnki_search_env.cache import SearchCache
from cnki_search_env.models import SearchStatus
from cnki_search_env.rate_limit import SerialSearchGate
from cnki_search_env.service import CnkiPublicSearchService

class ForbiddenSession:
    async def __aenter__(self):
        raise AssertionError('network session must not start after entry timeout')
    async def __aexit__(self, *_exc):
        return None

class SlowCache(SearchCache):
    def get(self, query, limit):
        time.sleep(.20)
        return super().get(query, limit)

async def assert_times_out(service):
    started = asyncio.get_running_loop().time()
    outcome = await service.search('topic')
    elapsed = asyncio.get_running_loop().time() - started
    assert outcome.status is SearchStatus.NETWORK_ERROR
    assert elapsed < .12, elapsed

async def main():
    catalog = Path(os.environ['CNKI_TEST_CATALOG'])
    original_validate = service_module.validate_catalog
    try:
        service_module.validate_catalog = lambda _path: time.sleep(.20)
        await assert_times_out(CnkiPublicSearchService(
            session_factory=ForbiddenSession,
            catalog=catalog,
            gate=SerialSearchGate(minimum_interval=0),
            search_timeout_seconds=.02,
        ))
        service_module.validate_catalog = lambda _path: None
        await assert_times_out(CnkiPublicSearchService(
            session_factory=ForbiddenSession,
            catalog=catalog,
            cache=SlowCache(),
            gate=SerialSearchGate(minimum_interval=0),
            search_timeout_seconds=.02,
        ))
    finally:
        service_module.validate_catalog = original_validate

asyncio.run(main())
"""
    for root in (ROOT / "scripts", ROOT / "mcpb" / "src"):
        completed = subprocess.run(
            [sys.executable, "-c", program],
            cwd=root,
            env=os.environ
            | {"PYTHONPATH": str(root), "CNKI_TEST_CATALOG": str(CATALOG)},
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr


def test_concurrent_network_starts_are_serial_and_six_seconds_apart() -> None:
    async def scenario() -> None:
        now = [0.0]
        starts: list[float] = []
        active = 0
        max_active = 0

        async def sleep(delay: float) -> None:
            now[0] += delay
            await asyncio.sleep(0)

        class Session:
            async def __aenter__(self):
                nonlocal active, max_active
                starts.append(now[0])
                active += 1
                max_active = max(max_active, active)
                return self

            async def __aexit__(self, *_exc):
                nonlocal active
                active -= 1

            async def search(self, _query):
                await asyncio.sleep(0)
                return type(
                    "Snapshot",
                    (),
                    {
                        "state_arguments": lambda self: {
                            "url": "https://kns.cnki.net/kns8s/defaultresult/index",
                            "title": "CNKI",
                            "visible_text": "未检索到相关文献",
                            "http_status": 200,
                            "has_result_table": False,
                        }
                    },
                )()

        service = CnkiPublicSearchService(
            session_factory=Session,
            catalog=CATALOG,
            gate=SerialSearchGate(
                minimum_interval=6.0,
                clock=lambda: now[0],
                sleep=sleep,
            ),
        )
        await asyncio.gather(service.search("first"), service.search("second"))
        assert starts == [0.0, 6.0]
        assert max_active == 1

    asyncio.run(scenario())


def test_fastmcp_tool_run_propagates_cancellation() -> None:
    async def scenario() -> None:
        from mcp.server.fastmcp import FastMCP

        started = asyncio.Event()

        class BlockingService:
            async def search(self, query: str, limit: int = 20) -> SearchOutcome:
                started.set()
                await asyncio.Event().wait()
                return SearchOutcome(
                    SearchStatus.NO_RESULTS, query, [], [], 0, [], "now"
                )

        server = CnkiMcpServer(service=BlockingService())
        mcp = server.build_fastmcp(FastMCP)
        tool = next(
            item
            for item in mcp._tool_manager.list_tools()
            if item.name == "cnki_search_env"
        )
        task = asyncio.create_task(tool.run({"query": "topic"}))
        await started.wait()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        else:
            raise AssertionError("FastMCP converted cancellation instead of propagating it")
        assert not server._tasks

    asyncio.run(scenario())
