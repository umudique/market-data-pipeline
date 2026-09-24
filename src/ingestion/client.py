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
from typing import Any, cast


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

    def __init__(self, provider: Any | None = None, source: str = "yfinance") -> None:
        if provider is None:
            import yfinance as yf_provider

            provider = yf_provider

        self._provider: Any = provider
        self._source = source

    def fetch(
        self,
        ticker: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """Return parsed provider bars for the requested ticker and range."""
        history = self._provider.Ticker(ticker).history(
            interval=interval,
            start=start,
            end=end,
            auto_adjust=False,
        )

        records: list[dict[str, Any]] = []
        for timestamp, row in history.iterrows():
            raw_payload = {
                "Open": self._to_python_value(row["Open"]),
                "High": self._to_python_value(row["High"]),
                "Low": self._to_python_value(row["Low"]),
                "Close": self._to_python_value(row["Close"]),
                "Volume": self._to_python_value(row["Volume"]),
            }
            records.append(
                {
                    "ticker": ticker,
                    "timestamp": self._to_datetime(timestamp),
                    "interval": interval,
                    "open": raw_payload["Open"],
                    "high": raw_payload["High"],
                    "low": raw_payload["Low"],
                    "close": raw_payload["Close"],
                    "volume": raw_payload["Volume"],
                    "source": self._source,
                    "raw_payload": raw_payload,
                }
            )

        return records

    @staticmethod
    def _to_datetime(value: Any) -> datetime:
        if hasattr(value, "to_pydatetime"):
            return cast(datetime, value.to_pydatetime())
        if isinstance(value, datetime):
            return value
        raise TypeError("provider timestamp must be datetime-like")

    @staticmethod
    def _to_python_value(value: Any) -> Any:
        if hasattr(value, "item"):
            return value.item()
        return value
