from __future__ import annotations

import pytest

from src.ingestion.rate_limit import RateLimitController

pytestmark = pytest.mark.unit


class FakeClock:
    def __init__(self) -> None:
        self.current = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.current

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.current += seconds


def test_rate_limit_enforces_spacing_before_each_provider_request() -> None:
    clock = FakeClock()
    controller = RateLimitController(
        calls_per_minute=2,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )

    controller.acquire()
    controller.acquire()
    controller.acquire()

    assert clock.sleeps == [30.0]


def test_rate_limit_rejects_non_positive_quota() -> None:
    with pytest.raises(ValueError):
        RateLimitController(calls_per_minute=0)
