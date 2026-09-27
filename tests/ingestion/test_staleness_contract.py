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


def test_stale_response_detection_accepts_daily_bar_on_last_expected_session() -> None:
    # 2026-01-02 is a Friday; daily bar present for that date → not stale
    detector = StalenessDetector()
    response_bars = [{"timestamp": datetime(2026, 1, 2, tzinfo=UTC), "close": 101.0}]

    assert (
        detector.is_stale(
            response_bars,
            requested_end=datetime(2026, 1, 2, tzinfo=UTC),
            interval="1d",
        )
        is False
    )


def test_stale_response_detection_flags_daily_bar_from_prior_session() -> None:
    # Latest bar is Thursday 2026-01-01; requested_end is Friday 2026-01-02 → stale
    detector = StalenessDetector()
    response_bars = [{"timestamp": datetime(2026, 1, 1, tzinfo=UTC), "close": 100.0}]

    assert (
        detector.is_stale(
            response_bars,
            requested_end=datetime(2026, 1, 2, tzinfo=UTC),
            interval="1d",
        )
        is True
    )


def test_stale_response_detection_accepts_weekly_bar_at_last_session() -> None:
    # Weekly bar dated on the last expected session (Fri 2026-01-09) → not stale
    detector = StalenessDetector()
    response_bars = [{"timestamp": datetime(2026, 1, 9, tzinfo=UTC), "close": 105.0}]

    assert (
        detector.is_stale(
            response_bars,
            requested_end=datetime(2026, 1, 9, tzinfo=UTC),
            interval="1wk",
        )
        is False
    )
