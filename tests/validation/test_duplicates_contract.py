from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IssueSeverity, IssueType
from src.validation.duplicates import DuplicateDetector

pytestmark = pytest.mark.unit


def test_duplicate_detector_flags_one_issue_per_duplicate_candle() -> None:
    batch_id = uuid.uuid4()
    timestamp = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)
    records = [
        {"ticker": "AAPL", "timestamp": timestamp},
        {"ticker": "AAPL", "timestamp": timestamp},
        {"ticker": "MSFT", "timestamp": timestamp},
    ]

    issues = DuplicateDetector().detect(records, batch_id=batch_id, source="yfinance")

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.DUPLICATE_CANDLE
    assert issues[0].severity is IssueSeverity.ERROR
    assert issues[0].ticker == "AAPL"
    assert issues[0].timestamp == timestamp
    assert issues[0].batch_id == batch_id
    assert issues[0].source == "yfinance"


def test_duplicate_detector_returns_zero_issues_for_distinct_timestamps() -> None:
    records = [
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC)},
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 31, tzinfo=UTC)},
    ]

    assert DuplicateDetector().detect(records, batch_id=uuid.uuid4(), source="yfinance") == []
