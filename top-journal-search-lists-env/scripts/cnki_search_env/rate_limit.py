from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable


class SerialSearchGate:
    """Serializes eligibility to begin browser searches."""

    def __init__(
        self,
        *,
        minimum_interval: float = 6.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.minimum_interval = minimum_interval
        self.clock = clock
        self.sleep = sleep
        self._last_started: float | None = None
        self._lock = asyncio.Lock()

    async def wait(self) -> float:
        async with self._lock:
            now = self.clock()
            delay = 0.0 if self._last_started is None else max(
                0.0, self.minimum_interval - (now - self._last_started)
            )
            if delay:
                await self.sleep(delay)
            self._last_started = self.clock()
            return delay
