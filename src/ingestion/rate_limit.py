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
        raise NotImplementedError

    def acquire(self) -> None:
        """Reserve one provider-call slot before a request is made."""
        raise NotImplementedError
