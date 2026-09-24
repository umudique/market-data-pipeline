from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IssueSeverity, IssueType
from src.validation.timestamps import TimestampValidator

pytestmark = pytest.mark.unit


def test_timestamp_validator_flags_none_timestamp() -> None:
    batch_id = uuid.uuid4()

    issues = TimestampValidator().validate(
        [{"ticker": "AAPL", "timestamp": None}],
        batch_id=batch_id,
        source="yfinance",
    )

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.INVALID_TIMESTAMP
    assert issues[0].severity is IssueSeverity.ERROR
    assert issues[0].ticker == "AAPL"
    assert issues[0].timestamp is None
    assert issues[0].batch_id == batch_id


def test_timestamp_validator_flags_timezone_naive_datetime() -> None:
    naive_timestamp = datetime(2026, 1, 2, 14, 30)

    issues = TimestampValidator().validate(
        [{"ticker": "AAPL", "timestamp": naive_timestamp}],
        batch_id=uuid.uuid4(),
        source="yfinance",
    )

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.INVALID_TIMESTAMP
    assert issues[0].severity is IssueSeverity.ERROR
    assert issues[0].timestamp == naive_timestamp


def test_timestamp_validator_returns_zero_issues_for_timezone_aware_datetime() -> None:
    records = [{"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC)}]

    assert TimestampValidator().validate(records, batch_id=uuid.uuid4(), source="yfinance") == []
