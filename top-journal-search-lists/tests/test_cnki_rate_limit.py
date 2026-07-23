import asyncio

from cnki_search.rate_limit import SerialSearchGate


def test_gate_waits_between_searches() -> None:
    values = iter([0.0, 0.0, 0.0, 6.0])
    delays: list[float] = []
    async def sleep(delay: float) -> None:
        delays.append(delay)
    gate = SerialSearchGate(minimum_interval=6.0, clock=lambda: next(values), sleep=sleep)
    assert asyncio.run(gate.wait()) == 0.0
    assert asyncio.run(gate.wait()) == 6.0
    assert delays == [6.0]


def test_default_minimum_interval_is_six_seconds() -> None:
    """合规约束：默认限速门必须是 6 秒。

    既有用例显式传入 minimum_interval=6.0，把默认值改成 0 也测不出来——
    审计的"限速门 6.0→0.0"变异体正因此存活。此处锁定默认值本身。
    """
    assert SerialSearchGate().minimum_interval == 6.0


def test_default_gate_actually_sleeps_between_consecutive_searches() -> None:
    values = iter([0.0, 0.0, 0.0, 0.0])
    delays: list[float] = []
    async def sleep(delay: float) -> None:
        delays.append(delay)
    gate = SerialSearchGate(clock=lambda: next(values), sleep=sleep)
    asyncio.run(gate.wait())
    asyncio.run(gate.wait())
    assert delays == [6.0]
