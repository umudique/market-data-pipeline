from __future__ import annotations

from datetime import UTC, datetime
from math import nan

import pytest

from src.normalization.numeric import NumericNormalizer

pytestmark = pytest.mark.unit


def _record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": "123.45",
        "high": "125.00",
        "low": "122.50",
        "close": "124.75",
        "volume": 1200,
    }
    record.update(overrides)
    return record


def test_numeric_normalizer_converts_ohlc_strings_and_integer_volume_to_float() -> None:
    assert NumericNormalizer().normalize(_record()) == {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": 123.45,
        "high": 125.0,
        "low": 122.5,
        "close": 124.75,
        "volume": 1200.0,
    }


def test_numeric_normalizer_rejects_nan_value() -> None:
    with pytest.raises(ValueError):
        NumericNormalizer().normalize(_record(close=nan))


def test_numeric_normalizer_rejects_unconvertible_value() -> None:
    with pytest.raises(ValueError):
        NumericNormalizer().normalize(_record(open="not-a-number"))
