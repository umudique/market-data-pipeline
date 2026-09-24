from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IssueSeverity, IssueType
from src.validation.stale import StaleDataValidator

pytestmark = pytest.mark.unit


def test_stale_data_validator_flags_latest_bar_before_requested_end() -> None:
    batch_id = uuid.uuid4()
    records = [
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC)},
        {"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 31, tzinfo=UTC)},
    ]

    issues = StaleDataValidator().validate(
        records,
        requested_end=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
        batch_id=batch_id,
        source="yfinance",
    )

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.STALE_RESPONSE
    assert issues[0].severity is IssueSeverity.WARNING
    assert issues[0].ticker == "AAPL"
    assert issues[0].timestamp == datetime(2026, 1, 2, 14, 31, tzinfo=UTC)
    assert issues[0].batch_id == batch_id


def test_stale_data_validator_returns_zero_issues_at_requested_end_boundary() -> None:
    records = [{"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 32, tzinfo=UTC)}]

    assert (
        StaleDataValidator().validate(
            records,
            requested_end=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
            batch_id=uuid.uuid4(),
            source="yfinance",
        )
        == []
    )
