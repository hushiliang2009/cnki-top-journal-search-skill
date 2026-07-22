from cnki_search.rate_limit import SerialSearchGate


def test_gate_waits_between_searches() -> None:
    values = iter([0.0, 0.0, 0.0, 6.0])
    delays: list[float] = []
    gate = SerialSearchGate(minimum_interval=6.0, clock=lambda: next(values), sleep=delays.append)
    assert gate.wait() == 0.0
    assert gate.wait() == 6.0
    assert delays == [6.0]
