from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from src.ingestion.client import MarketDataClient

pytestmark = pytest.mark.unit


def test_successful_provider_response_parsing_uses_deterministic_fixture() -> None:
    provider_calls: list[dict[str, object]] = []
    index = pd.to_datetime(
        ["2026-01-02T14:30:00Z", "2026-01-02T14:31:00Z"],
        utc=True,
    )
    history = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.5, 100.5],
            "Close": [101.5, 102.5],
            "Volume": [1200, 1300],
        },
        index=index,
    )

    class FakeTicker:
        def __init__(self, ticker: str) -> None:
            self.ticker = ticker

        def history(
            self,
            *,
            interval: str,
            start: datetime,
            end: datetime,
            auto_adjust: bool,
        ) -> pd.DataFrame:
            provider_calls.append(
                {
                    "ticker": self.ticker,
                    "interval": interval,
                    "start": start,
                    "end": end,
                    "auto_adjust": auto_adjust,
                }
            )
            return history

    class FakeYFinance:
        Ticker = FakeTicker

    client = MarketDataClient(provider=FakeYFinance(), source="yfinance")

    records = client.fetch(
        "AAPL",
        "1m",
        datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
    )

    assert provider_calls == [
        {
            "ticker": "AAPL",
            "interval": "1m",
            "start": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
            "end": datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
            "auto_adjust": False,
        }
    ]
    assert records == [
        {
            "ticker": "AAPL",
            "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
            "interval": "1m",
            "open": 100.0,
            "high": 102.0,
            "low": 99.5,
            "close": 101.5,
            "volume": 1200,
            "source": "yfinance",
            "raw_payload": {
                "Open": 100.0,
                "High": 102.0,
                "Low": 99.5,
                "Close": 101.5,
                "Volume": 1200,
            },
        },
        {
            "ticker": "AAPL",
            "timestamp": datetime(2026, 1, 2, 14, 31, tzinfo=UTC),
            "interval": "1m",
            "open": 101.0,
            "high": 103.0,
            "low": 100.5,
            "close": 102.5,
            "volume": 1300,
            "source": "yfinance",
            "raw_payload": {
                "Open": 101.0,
                "High": 103.0,
                "Low": 100.5,
                "Close": 102.5,
                "Volume": 1300,
            },
        },
    ]
