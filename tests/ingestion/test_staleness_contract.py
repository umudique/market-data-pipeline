from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.ingestion.staleness import StalenessDetector

pytestmark = pytest.mark.unit


def test_stale_response_detection_returns_true_beyond_freshness_boundary() -> None:
    detector = StalenessDetector()
    response_bars = [
        {"timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC), "close": 101.5},
        {"timestamp": datetime(2026, 1, 2, 14, 31, tzinfo=UTC), "close": 102.5},
    ]

    assert (
        detector.is_stale(
            response_bars,
            requested_end=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
        )
        is True
    )


def test_stale_response_detection_accepts_current_boundary_timestamp() -> None:
    detector = StalenessDetector()
    response_bars = [
        {"timestamp": datetime(2026, 1, 2, 14, 32, tzinfo=UTC), "close": 102.5},
    ]

    assert (
        detector.is_stale(
            response_bars,
            requested_end=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
        )
        is False
    )
