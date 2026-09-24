from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.domain import MarketBar, ValidationStatus
from src.screener.calculations import RelativeVolumeCalculator

pytestmark = pytest.mark.unit


def _bar(timestamp: datetime, volume: float) -> MarketBar:
    return MarketBar(
        ticker="AAPL",
        timestamp=timestamp,
        interval="1d",
        open=100.0,
        high=105.0,
        low=99.0,
        close=104.0,
        volume=volume,
        source="yfinance",
        ingestion_batch_id=uuid.uuid4(),
        validated=True,
        validation_status=ValidationStatus.VALID,
    )


def test_relative_volume_calculator_uses_historical_mean_volume() -> None:
    timestamp = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)
    historical_bars = [
        _bar(timestamp - timedelta(days=2), 1_000_000.0),
        _bar(timestamp - timedelta(days=1), 1_000_000.0),
    ]

    result = RelativeVolumeCalculator().calculate(
        earnings_volume=2_000_000.0,
        historical_bars=historical_bars,
    )

    assert result == 2.0


def test_relative_volume_calculator_rejects_empty_history() -> None:
    with pytest.raises((ZeroDivisionError, ValueError)):
        RelativeVolumeCalculator().calculate(
            earnings_volume=2_000_000.0,
            historical_bars=[],
        )
