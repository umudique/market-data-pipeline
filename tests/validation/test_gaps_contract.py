from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IssueSeverity, IssueType
from src.validation.gaps import IntervalGapDetector

pytestmark = pytest.mark.unit


def test_interval_gap_detector_flags_one_missing_interval_issue_per_missing_bar() -> None:
    batch_id = uuid.uuid4()
    records = [
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC)},
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 32, tzinfo=UTC)},
    ]

    issues = IntervalGapDetector().detect(
        records,
        interval="1m",
        expected_start=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        expected_end=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
        ticker="AAPL",
        batch_id=batch_id,
        source="yfinance",
    )

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.MISSING_INTERVAL
    assert issues[0].severity is IssueSeverity.WARNING
    assert issues[0].ticker == "AAPL"
    assert issues[0].timestamp == datetime(2026, 1, 2, 14, 31, tzinfo=UTC)
    assert issues[0].batch_id == batch_id
    assert issues[0].source == "yfinance"


def test_interval_gap_detector_returns_zero_issues_for_complete_sequence() -> None:
    records = [
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC)},
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 31, tzinfo=UTC)},
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 32, tzinfo=UTC)},
    ]

    assert (
        IntervalGapDetector().detect(
            records,
            interval="1m",
            expected_start=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
            expected_end=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
            ticker="AAPL",
            batch_id=uuid.uuid4(),
            source="yfinance",
        )
        == []
    )
