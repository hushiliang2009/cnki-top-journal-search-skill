from __future__ import annotations

import time
from collections.abc import Callable


class SerialSearchGate:
    def __init__(
        self, *, minimum_interval: float = 6.0, clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if minimum_interval < 6.0:
            raise ValueError("minimum_interval must be at least 6 seconds")
        self.minimum_interval = minimum_interval
        self.clock = clock
        self.sleep = sleep
        self._last_started: float | None = None

    def wait(self) -> float:
        now = self.clock()
        delay = 0.0 if self._last_started is None else max(0.0, self.minimum_interval - (now - self._last_started))
        if delay:
            self.sleep(delay)
        self._last_started = self.clock()
        return delay
