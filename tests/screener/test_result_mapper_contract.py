from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import EarningsGapResult, MarketBar, ValidationStatus
from src.screener.result import ScreenerResultMapper

pytestmark = pytest.mark.unit


def test_screener_result_mapper_returns_exact_domain_result() -> None:
    timestamp = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)
    bar = MarketBar(
        ticker="AAPL",
        timestamp=timestamp,
        interval="1d",
        open=110.0,
        high=115.0,
        low=108.0,
        close=112.0,
        volume=2_000_000.0,
        source="yfinance",
        ingestion_batch_id=uuid.uuid4(),
        validated=True,
        validation_status=ValidationStatus.VALID,
    )

    result = ScreenerResultMapper().map(
        bar,
        gap_percent=10.0,
        relative_volume=2.0,
        close_return=1.8181818181818181,
    )

    assert result == EarningsGapResult(
        ticker="AAPL",
        date=timestamp,
        gap_percent=10.0,
        relative_volume=2.0,
        close_return=1.8181818181818181,
        validated=True,
    )
