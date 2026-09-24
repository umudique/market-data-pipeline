"""Provider-specific HTTP requests and response parsing.

Contract:
    `MarketDataClient` is the only ingestion component allowed to call
    `yfinance` or any provider-specific API. It converts provider responses
    into deterministic source-record dictionaries while preserving enough raw
    provider metadata for auditability.

Invariants:
    The client does not validate, normalize, persist, or silently repair market
    data. Empty, malformed, stale, or otherwise suspect responses remain visible
    to downstream ingestion and validation components.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class MarketDataClient:
    """Fetch and parse market data from the configured provider.

    Preconditions:
        `ticker`, `interval`, `start`, and `end` identify one provider request.
        `start` must be earlier than `end`.

    Postconditions:
        Returns source-record dictionaries with provider payload fields mapped
        to stable ingestion keys, including ticker, timestamp, OHLCV values,
        interval, source, and raw provider payload. No live provider call is made
        anywhere outside this class.
    """

    def __init__(self, provider: Any, source: str) -> None:
        raise NotImplementedError

    def fetch(
        self,
        ticker: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """Return parsed provider bars for the requested ticker and range."""
        raise NotImplementedError
