"""Provider-specific HTTP requests and response parsing (yfinance)."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class MarketDataClient:
    def fetch(
        self,
        ticker: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError
