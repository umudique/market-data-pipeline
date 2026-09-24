from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta, timezone

import pytest

from src.domain import IssueSeverity, IssueType
from src.validation.timezone import TimezoneValidator

pytestmark = pytest.mark.unit


def test_timezone_validator_flags_non_utc_timezone() -> None:
    batch_id = uuid.uuid4()
    timestamp = datetime(2026, 1, 2, 9, 30, tzinfo=timezone(timedelta(hours=-5)))

    issues = TimezoneValidator(canonical_timezone="UTC").validate(
        [{"ticker": "AAPL", "timestamp": timestamp}],
        batch_id=batch_id,
        source="yfinance",
    )

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.TIMEZONE_NORMALIZATION_REQUIRED
    assert issues[0].severity is IssueSeverity.WARNING
    assert issues[0].ticker == "AAPL"
    assert issues[0].timestamp == timestamp
    assert issues[0].batch_id == batch_id


def test_timezone_validator_returns_zero_issues_for_utc_timestamp() -> None:
    records = [{"ticker": "AAPL", "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC)}]

    assert (
        TimezoneValidator(canonical_timezone="UTC").validate(
            records,
            batch_id=uuid.uuid4(),
            source="yfinance",
        )
        == []
    )
