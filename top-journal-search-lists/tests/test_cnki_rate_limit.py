import pytest

from cnki_search.rate_limit import SerialRateLimiter


class FakeSleep:
    def __init__(self) -> None:
        self.calls: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


def test_search_delay_uses_four_to_seven_seconds() -> None:
    fake_sleep = FakeSleep()
    limiter = SerialRateLimiter(sleep=fake_sleep, uniform=lambda low, high: 5.5)
    limiter.wait("search_page")
    assert fake_sleep.calls == [5.5]


def test_call_limits_are_enforced_before_work() -> None:
    limiter = SerialRateLimiter(sleep=lambda _: None, uniform=lambda low, high: low)
    limiter.validate_count("download", 5)
    with pytest.raises(ValueError, match="最多 5"):
        limiter.validate_count("download", 6)
