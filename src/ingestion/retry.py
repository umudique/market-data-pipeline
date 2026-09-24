"""Bounded retry behaviour for retryable provider failures.

Contract:
    `RetryPolicy` executes a callable until it succeeds, reaches the configured
    maximum attempt count, or raises a non-retryable exception.

Invariants:
    Retry attempts are bounded. Retryable provider failures may be retried with
    configured backoff, but validation/data-quality defects are terminal unless
    an explicit provider contract makes retry meaningful.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RetryPolicy:
    """Apply bounded retry behavior around provider calls.

    Preconditions:
        `max_attempts` is a positive integer. `backoff_seconds` is non-negative.

    Postconditions:
        A successful callable result is returned unchanged. Retryable failures
        are attempted no more than `max_attempts` times. Non-retryable failures
        are raised immediately without additional attempts.
    """

    def __init__(
        self,
        max_attempts: int,
        backoff_seconds: float,
        retryable_exceptions: tuple[type[BaseException], ...] = (),
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if backoff_seconds < 0:
            raise ValueError("backoff_seconds must be non-negative")

        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds
        self._retryable_exceptions = retryable_exceptions
        self._sleep = sleep

    def execute(self, fn: F, *args: Any, **kwargs: Any) -> Any:
        """Execute `fn` under the retry contract."""
        attempt = 0
        while True:
            try:
                return fn(*args, **kwargs)
            except self._retryable_exceptions:
                attempt += 1
                if attempt >= self._max_attempts:
                    raise
                self._sleep(self._backoff_seconds)
