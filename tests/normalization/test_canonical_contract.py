from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import MarketBar, ValidationStatus
from src.normalization.canonical import RecordCanonicalizer

pytestmark = pytest.mark.unit


def test_record_canonicalizer_returns_market_bar_with_exact_values() -> None:
    batch_id = uuid.uuid4()
    timestamp = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)
    record = {
        "ticker": "AAPL",
        "timestamp": timestamp,
        "interval": "1m",
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 1200.0,
    }

    bar = RecordCanonicalizer().canonicalize(record, batch_id=batch_id, source="yfinance")

    assert isinstance(bar, MarketBar)
    assert bar == MarketBar(
        ticker="AAPL",
        timestamp=timestamp,
        interval="1m",
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        volume=1200.0,
        source="yfinance",
        ingestion_batch_id=batch_id,
        validated=True,
        validation_status=ValidationStatus.VALID,
    )
    assert bar.validation_status is ValidationStatus.VALID
