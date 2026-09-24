from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import MarketBar, ValidationStatus
from src.normalization.canonical import NormalizationResultBuilder

pytestmark = pytest.mark.unit


def _bar(batch_id: uuid.UUID, ticker: str = "AAPL") -> MarketBar:
    return MarketBar(
        ticker=ticker,
        timestamp=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
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


def test_normalization_result_builder_returns_same_ordered_market_bars_with_batch_id() -> None:
    batch_id = uuid.uuid4()
    bars = [_bar(batch_id, "AAPL"), _bar(batch_id, "MSFT")]

    result = NormalizationResultBuilder().build(bars, batch_id=batch_id)

    assert result == bars
    assert [bar.ingestion_batch_id for bar in result] == [batch_id, batch_id]


def test_normalization_result_builder_returns_empty_list_for_empty_input() -> None:
    assert NormalizationResultBuilder().build([], batch_id=uuid.uuid4()) == []
