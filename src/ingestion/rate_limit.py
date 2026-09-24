"""Rate-limit enforcement — prevents exceeding provider call quotas."""

from __future__ import annotations


class RateLimitController:
    def __init__(self, calls_per_minute: int) -> None:
        raise NotImplementedError

    def acquire(self) -> None:
        raise NotImplementedError
