from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.domain import EarningsGapScreenerRequest
from src.screener.request import ScreenerRequestValidator

pytestmark = pytest.mark.unit


def test_screener_request_validator_rejects_invalid_date_range() -> None:
    request = EarningsGapScreenerRequest(
        start_date=datetime(2026, 1, 3, tzinfo=UTC),
        end_date=datetime(2026, 1, 2, tzinfo=UTC),
        minimum_gap=5.0,
        minimum_volume=1_000_000.0,
        ticker_universe=["AAPL"],
    )

    with pytest.raises(ValueError):
        ScreenerRequestValidator().validate(request)


def test_screener_request_validator_accepts_valid_request() -> None:
    request = EarningsGapScreenerRequest(
        start_date=datetime(2026, 1, 2, tzinfo=UTC),
        end_date=datetime(2026, 1, 3, tzinfo=UTC),
        minimum_gap=5.0,
        minimum_volume=1_000_000.0,
        ticker_universe=["AAPL"],
    )

    ScreenerRequestValidator().validate(request)
