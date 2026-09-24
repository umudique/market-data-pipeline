"""Rate-limit enforcement for provider calls.

Contract:
    `RateLimitController` grants permission before every provider request and
    blocks or delays calls that would exceed the configured provider quota.

Invariants:
    Ingestion code acquires rate-limit permission before each external request.
    The controller never performs provider calls and never changes market data.
"""

from __future__ import annotations

import time
from collections.abc import Callable


class RateLimitController:
    """Control request pacing for the external provider.

    Preconditions:
        `calls_per_minute` is a positive integer.

    Postconditions:
        `acquire` returns only when one request is permitted under the quota.
        Deterministic clocks/sleepers may be injected by tests so call spacing
        can be verified without wall-clock delays.
    """

    def __init__(
        self,
        calls_per_minute: int,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if calls_per_minute <= 0:
            raise ValueError("calls_per_minute must be positive")

        self._calls_per_minute = calls_per_minute
        self._interval_seconds = 60.0 / calls_per_minute
        self._monotonic = monotonic
        self._sleep = sleep
        self._tokens = float(calls_per_minute)
        self._last_refill = monotonic()

    def acquire(self) -> None:
        """Reserve one provider-call slot before a request is made."""
        self._refill()
        if self._tokens < 1.0:
            wait_seconds = self._interval_seconds * (1.0 - self._tokens)
            self._sleep(wait_seconds)
            self._refill()

        self._tokens -= 1.0

    def _refill(self) -> None:
        now = self._monotonic()
        elapsed = now - self._last_refill
        if elapsed <= 0:
            return

        self._tokens = min(
            float(self._calls_per_minute),
            self._tokens + (elapsed / self._interval_seconds),
        )
        self._last_refill = now
