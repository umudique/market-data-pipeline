from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.normalization.schema import SchemaNormalizer

pytestmark = pytest.mark.unit


def test_schema_normalizer_preserves_canonical_market_bar_fields() -> None:
    record = {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 1200.0,
    }

    assert SchemaNormalizer().normalize(record) == record


def test_schema_normalizer_discards_unknown_fields() -> None:
    record = {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 1200.0,
        "provider_note": "discard me",
    }

    assert SchemaNormalizer().normalize(record) == {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 1200.0,
    }
