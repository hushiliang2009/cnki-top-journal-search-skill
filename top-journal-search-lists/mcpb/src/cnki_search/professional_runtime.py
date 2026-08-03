"""WebVPN 专业检索的默认生产运行时。"""
from __future__ import annotations

import asyncio
import contextlib
import os
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from .browser import await_maybe
from .models import SearchStatus
from .professional import ExpressionBatch, PlanExecutionResult
from .professional_service import CnkiProfessionalSearchService
from .webvpn import (
    CAPTCHA_TEXT_MARKERS,
    CAPTCHA_VIEWPORT_JS,
    BatchCheckpoint,
    ProfessionalSearchPage,
    Throttle,
    WebVpnConfig,
    WebVpnSession,
    _finish_cleanup_bounded,
)


def default_state_dir() -> Path:
    """返回节流和脱敏断点的状态目录，不创建浏览器配置。"""
    return Path.home() / ".cnki-search"


class ProfessionalSearchRuntime:
    def __init__(
        self, session: WebVpnSession, service: CnkiProfessionalSearchService
    ) -> None:
        self.session = session
        self.service = service
        self._lock = asyncio.Lock()
        self._closed = False

    async def search_group(
        self,
        topic: str,
        group: str,
        *,
        limit: int,
        year_from: int | None,
        year_to: int | None,
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("WebVPN 专业检索运行时已关闭")
        async with self._lock:
            self.session.ensure_open()
            return await self.service.search_group(
                topic,
                group,
                limit=limit,
                year_from=year_from,
                year_to=year_to,
            )

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            await self.session.close()


class ProfessionalBatchExecutor:
    """为每个表达式从保留的知网首页新开并管理结果标签页。"""

    def __init__(
        self,
        session: WebVpnSession,
        *,
        challenge_timeout_seconds: float = 600.0,
        challenge_poll_seconds: float = 2.0,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self.session = session
        self.challenge_timeout_seconds = challenge_timeout_seconds
        self.challenge_poll_seconds = challenge_poll_seconds
        self._sleep = sleep
        self._now = now
        self.active_challenge_page: Any = None

    async def __call__(
        self, plan: ExpressionBatch
    ) -> PlanExecutionResult:
        self.session.ensure_open()
        home_page = self.session.page
        driver = ProfessionalSearchPage(home_page)
        result_page: Any = None
        retain_challenge = False
        try:
            result_page = await driver.open_from_home(
                self.session.context, preserve_home=True
            )
            await driver.switch_to_professional()
            executed = await driver.execute_plan(plan)
            result = (
                executed
                if isinstance(executed, PlanExecutionResult)
                else PlanExecutionResult(*executed)
            )
            if result.status == SearchStatus.CHALLENGE_DETECTED.value:
                self.active_challenge_page = result_page
                retain_challenge = True
            return PlanExecutionResult(
                status=result.status,
                html=result.html,
                url="",
                source_category_applied=result.source_category_applied,
                source_category_total=result.source_category_total,
            )
        finally:
            if (
                result_page is not None
                and result_page is not home_page
                and not retain_challenge
            ):
                await self._close_page(result_page)

    async def wait_for_manual_challenge(
        self, _plan: ExpressionBatch
    ) -> bool:
        """只观察安全验证是否消失，不操作验证页。"""
        page = self.active_challenge_page
        if page is None:
            return False
        logical_deadline = self._now() + self.challenge_timeout_seconds
        loop = asyncio.get_running_loop()
        overall_deadline = loop.time() + self.challenge_timeout_seconds
        cleanup_reserve = min(
            5.0,
            self.challenge_timeout_seconds / 2,
        )
        observation_timeout = max(
            self.challenge_timeout_seconds - cleanup_reserve,
            0.0,
        )
        result = False
        try:
            try:
                async with asyncio.timeout(observation_timeout):
                    result = await self._observe_challenge(
                        page,
                        logical_deadline,
                    )
            except TimeoutError:
                result = False
        finally:
            if self.active_challenge_page is page:
                self.active_challenge_page = None
            remaining = max(overall_deadline - loop.time(), 0.0)
            closed, cancellation = await _finish_cleanup_bounded(
                self._close_page(page),
                min(remaining, cleanup_reserve),
            )
            if cancellation is not None:
                raise cancellation
            if not closed:
                result = False
        return result

    async def _observe_challenge(
        self,
        page: Any,
        deadline: float,
    ) -> bool:
        while self._now() <= deadline:
            is_closed = getattr(page, "is_closed", None)
            if callable(is_closed) and is_closed():
                return False
            try:
                visible = await await_maybe(
                    page.evaluate(
                        CAPTCHA_VIEWPORT_JS,
                        list(CAPTCHA_TEXT_MARKERS),
                    )
                )
            except Exception:
                return False
            if not visible:
                return True
            remaining = deadline - self._now()
            if remaining <= 0:
                return False
            await self._sleep(
                min(self.challenge_poll_seconds, remaining)
            )
        return False

    @staticmethod
    async def _close_page(page: Any) -> None:
        with contextlib.suppress(Exception, asyncio.CancelledError):
            await await_maybe(page.close())


async def build_professional_runtime_from_env() -> ProfessionalSearchRuntime:
    home_url = (os.environ.get("CNKI_WEBVPN_HOME") or "").strip()
    if not home_url:
        raise ValueError("请设置 CNKI_WEBVPN_HOME")
    session = WebVpnSession(WebVpnConfig(home_url))
    try:
        await session.__aenter__()
        await session.wait_until_ready()
        executor = ProfessionalBatchExecutor(session)
        state_dir = default_state_dir()
        service = CnkiProfessionalSearchService(
            executor,
            throttle=Throttle(state_dir / "throttle"),
            checkpoint=BatchCheckpoint(state_dir / "checkpoint.json"),
            on_challenge=executor.wait_for_manual_challenge,
        )
        return ProfessionalSearchRuntime(session, service)
    except BaseException:
        await session.close()
        raise


__all__ = [
    "ProfessionalBatchExecutor",
    "ProfessionalSearchRuntime",
    "build_professional_runtime_from_env",
    "default_state_dir",
]
