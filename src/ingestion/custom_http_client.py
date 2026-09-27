"""HTTP client for user-supplied OHLCV APIs.

Expected response format — JSON array:
    [
        {
            "ticker":    "AAPL",
            "timestamp": "2024-01-02T00:00:00",
            "open":      185.0,
            "high":      188.0,
            "low":       184.0,
            "close":     187.0,
            "volume":    1000000
        },
        ...
    ]

URL template placeholders (all optional):
    {ticker}    — ticker symbol
    {start}     — ISO-8601 start datetime
    {end}       — ISO-8601 end datetime
    {interval}  — interval string, e.g. "1d"
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

import requests


def custom_source_id(url_template: str) -> str:
    """Return a stable source identity for a user-supplied provider URL."""
    return f"custom:{hashlib.sha256(url_template.encode()).hexdigest()[:12]}"


class CustomHttpClient:
    """Fetch OHLCV data from a user-supplied HTTP endpoint."""

    def __init__(self, url_template: str, api_key: str | None = None) -> None:
        self._url_template = url_template
        self.source = custom_source_id(url_template)
        self._headers: dict[str, str] = {}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    def fetch(
        self,
        ticker: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        url = self._url_template.format(
            ticker=ticker,
            start=start.isoformat(),
            end=end.isoformat(),
            interval=interval,
        )
        response = requests.get(url, headers=self._headers, timeout=30)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list):
            raise ValueError(f"Custom API must return a JSON array, got {type(payload).__name__}")

        records: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                records.append(
                    {
                        "ticker": ticker,
                        "timestamp": None,
                        "interval": interval,
                        "open": None,
                        "high": None,
                        "low": None,
                        "close": None,
                        "volume": None,
                        "source": self.source,
                        "raw_payload": item,
                    }
                )
                continue

            raw = dict(item)
            records.append(
                {
                    "ticker": str(item.get("ticker", ticker)),
                    "timestamp": self._parse_timestamp(item.get("timestamp")),
                    "interval": interval,
                    "open": self._optional_float(item.get("open")),
                    "high": self._optional_float(item.get("high")),
                    "low": self._optional_float(item.get("low")),
                    "close": self._optional_float(item.get("close")),
                    "volume": self._optional_float(item.get("volume")),
                    "source": self.source,
                    "raw_payload": raw,
                }
            )
        return records

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=UTC)
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
