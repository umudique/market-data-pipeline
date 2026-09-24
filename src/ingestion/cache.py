"""Optional short-lived API response cache (Redis-backed).

Only activated when REDIS_URL is configured. PostgreSQL remains the
source of truth — this cache never bypasses validation.
"""

from __future__ import annotations

from typing import Any


class ResponseCache:
    def get(self, key: str) -> Any | None:
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        raise NotImplementedError

    @staticmethod
    def build_key(ticker: str, interval: str, start: str, end: str) -> str:
        raise NotImplementedError
