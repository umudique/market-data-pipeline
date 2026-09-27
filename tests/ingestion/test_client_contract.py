from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from src.ingestion.client import MarketDataClient
from src.ingestion.custom_http_client import CustomHttpClient

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


def test_custom_http_client_preserves_bad_rows_for_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[object]:
            return [
                {
                    "ticker": "AAPL",
                    "timestamp": "2026-01-02T14:30:00",
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                },
                ["not", "a", "mapping"],
            ]

    monkeypatch.setattr(
        "src.ingestion.custom_http_client.requests.get", lambda *a, **k: FakeResponse()
    )

    records = CustomHttpClient("https://vendor-a.example/{ticker}").fetch(
        "AAPL",
        "1m",
        datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        datetime(2026, 1, 2, 14, 31, tzinfo=UTC),
    )

    assert len(records) == 2
    assert records[0]["volume"] is None
    assert records[0]["timestamp"] == datetime(2026, 1, 2, 14, 30)
    assert records[1]["open"] is None
    assert records[1]["raw_payload"] == ["not", "a", "mapping"]


def test_custom_http_client_source_distinguishes_url_templates() -> None:
    first = CustomHttpClient("https://vendor-a.example/{ticker}")
    second = CustomHttpClient("https://vendor-b.example/{ticker}")

    assert first.source != second.source
    assert first.source.startswith("custom:")


def test_custom_http_client_expands_all_url_placeholders(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> list[object]:
            return []

    def fake_get(url: str, **kwargs: object) -> FakeResponse:
        captured.append(url)
        return FakeResponse()

    monkeypatch.setattr("src.ingestion.custom_http_client.requests.get", fake_get)

    start = datetime(2026, 1, 2, tzinfo=UTC)
    end = datetime(2026, 1, 3, tzinfo=UTC)
    CustomHttpClient("https://api.example/{ticker}/{interval}?from={start}&to={end}").fetch(
        "AAPL", "1d", start, end
    )

    assert len(captured) == 1
    assert "AAPL" in captured[0]
    assert "1d" in captured[0]
    assert start.isoformat() in captured[0]
    assert end.isoformat() in captured[0]


def test_custom_http_client_sends_bearer_token_when_api_key_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_headers: list[dict[str, str]] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> list[object]:
            return []

    def fake_get(url: str, headers: dict[str, str], **kwargs: object) -> FakeResponse:
        captured_headers.append(headers)
        return FakeResponse()

    monkeypatch.setattr("src.ingestion.custom_http_client.requests.get", fake_get)

    CustomHttpClient("https://api.example/{ticker}", api_key="secret-token").fetch(
        "AAPL", "1d", datetime(2026, 1, 2, tzinfo=UTC), datetime(2026, 1, 3, tzinfo=UTC)
    )

    assert captured_headers[0].get("Authorization") == "Bearer secret-token"


def test_custom_http_client_raises_on_non_list_json_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"error": "unexpected shape"}

    monkeypatch.setattr(
        "src.ingestion.custom_http_client.requests.get", lambda *a, **k: FakeResponse()
    )

    with pytest.raises(ValueError, match="JSON array"):
        CustomHttpClient("https://api.example/{ticker}").fetch(
            "AAPL", "1d", datetime(2026, 1, 2, tzinfo=UTC), datetime(2026, 1, 3, tzinfo=UTC)
        )
