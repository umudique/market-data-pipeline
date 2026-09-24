from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IngestionBatch
from src.validation.orchestrator import ValidationOrchestrator

pytestmark = pytest.mark.unit


def _batch() -> IngestionBatch:
    return IngestionBatch(
        batch_id=uuid.uuid4(),
        source="yfinance",
        requested_range="2026-01-02T14:30:00+00:00/2026-01-02T14:31:00+00:00",
    )


def _record(timestamp: datetime) -> dict[str, object]:
    return {
        "ticker": "AAPL",
        "timestamp": timestamp,
        "interval": "1m",
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 1200,
        "source": "yfinance",
    }


def test_validation_orchestrator_returns_all_count_keys_for_clean_batch() -> None:
    counts, issues = ValidationOrchestrator().validate(
        _batch(),
        [
            _record(datetime(2026, 1, 2, 14, 30, tzinfo=UTC)),
            _record(datetime(2026, 1, 2, 14, 31, tzinfo=UTC)),
        ],
    )

    assert counts == {
        "valid": 2,
        "invalid": 0,
        "duplicates": 0,
        "missing_intervals": 0,
        "idempotent_conflicts": 0,
    }
    assert issues == []


def test_validation_orchestrator_counts_duplicate_candles() -> None:
    timestamp = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)

    counts, issues = ValidationOrchestrator().validate(
        _batch(), [_record(timestamp), _record(timestamp)]
    )

    assert counts["duplicates"] == 1
    assert set(counts) == {
        "valid",
        "invalid",
        "duplicates",
        "missing_intervals",
        "idempotent_conflicts",
    }
    assert len(issues) > 0
