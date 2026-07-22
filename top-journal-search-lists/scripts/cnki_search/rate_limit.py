from __future__ import annotations

import random
import time
from collections.abc import Callable


class SerialRateLimiter:
    _DELAYS = {
        "search_page": (4.0, 7.0),
        "detail": (3.0, 6.0),
        "download": (8.0, 15.0),
    }
    _LIMITS = {"search_page": 3, "detail": 10, "download": 5}

    def __init__(
        self,
        *,
        sleep: Callable[[float], None] = time.sleep,
        uniform: Callable[[float, float], float] = random.uniform,
    ) -> None:
        self._sleep = sleep
        self._uniform = uniform

    def wait(self, kind: str) -> float:
        try:
            low, high = self._DELAYS[kind]
        except KeyError as exc:
            raise ValueError(f"未知限流类型: {kind}") from exc
        seconds = self._uniform(low, high)
        self._sleep(seconds)
        return seconds

    def validate_count(self, kind: str, count: int) -> None:
        try:
            maximum = self._LIMITS[kind]
        except KeyError as exc:
            raise ValueError(f"未知调用类型: {kind}") from exc
        if count < 0 or count > maximum:
            raise ValueError(f"{kind} 单次最多 {maximum} 条")

