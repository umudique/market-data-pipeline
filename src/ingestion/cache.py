"""Optional short-lived API response cache (Redis-backed).

Only activated when REDIS_URL is configured. PostgreSQL remains the
source of truth — this cache never bypasses validation.
"""

from __future__ import annotations

from typing import Any


class ResponseCache:
    """Optional short-lived cache for provider responses.

    Preconditions:
        The cache is active only when `REDIS_URL` is configured by application
        settings. Cache keys include all request dimensions that affect provider
        output.

    Postconditions:
        Cached payloads are returned exactly as source responses and must still
        pass staleness validation before acceptance. Cache misses return `None`.
    """

    def get(self, key: str) -> Any | None:
        """Return a cached provider payload, or `None` when absent/inactive."""
        return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store a source payload for a bounded TTL when caching is active."""
        return None

    @staticmethod
    def build_key(ticker: str, interval: str, start: str, end: str) -> str:
        """Build a cache key from every provider-output request dimension."""
        return f"market-data:{ticker}:{interval}:{start}:{end}"
