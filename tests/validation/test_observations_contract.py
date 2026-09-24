from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IssueSeverity, IssueType
from src.validation.observations import ObservationValidator

pytestmark = pytest.mark.unit


def test_observation_validator_flags_missing_volume_key() -> None:
    batch_id = uuid.uuid4()
    record = {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
    }

    issues = ObservationValidator().validate([record], batch_id=batch_id, source="yfinance")

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.MISSING_OBSERVATION
    assert issues[0].severity is IssueSeverity.ERROR
    assert issues[0].ticker == "AAPL"
    assert issues[0].timestamp == datetime(2026, 1, 2, 14, 30, tzinfo=UTC)
    assert issues[0].batch_id == batch_id


def test_observation_validator_returns_zero_issues_when_all_required_fields_exist() -> None:
    record = {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 1200,
    }

    assert ObservationValidator().validate([record], batch_id=uuid.uuid4(), source="yfinance") == []
