from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IssueSeverity, IssueType
from src.validation.prices import PriceValidator

pytestmark = pytest.mark.unit


def _record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "ticker": "AAPL",
        "timestamp": datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
    }
    record.update(overrides)
    return record


def test_price_validator_flags_zero_open() -> None:
    batch_id = uuid.uuid4()

    issues = PriceValidator().validate([_record(open=0.0)], batch_id=batch_id, source="yfinance")

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.INVALID_PRICE
    assert issues[0].severity is IssueSeverity.ERROR
    assert issues[0].ticker == "AAPL"
    assert issues[0].batch_id == batch_id


def test_price_validator_flags_negative_close() -> None:
    issues = PriceValidator().validate(
        [_record(close=-1.0)],
        batch_id=uuid.uuid4(),
        source="yfinance",
    )

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.INVALID_PRICE
    assert issues[0].severity is IssueSeverity.ERROR


def test_price_validator_returns_zero_issues_for_positive_ohlc() -> None:
    assert PriceValidator().validate([_record()], batch_id=uuid.uuid4(), source="yfinance") == []


def test_price_validator_flags_ohlc_inconsistency_when_high_below_low() -> None:
    batch_id = uuid.uuid4()

    issues = PriceValidator().validate(
        [_record(high=98.0, low=99.0)],
        batch_id=batch_id,
        source="yfinance",
    )

    assert len(issues) == 1
    assert issues[0].issue_type is IssueType.OHLC_INCONSISTENCY
    assert issues[0].severity is IssueSeverity.ERROR
    assert issues[0].ticker == "AAPL"
    assert issues[0].batch_id == batch_id


def test_price_validator_does_not_flag_ohlc_inconsistency_when_high_equals_low() -> None:
    issues = PriceValidator().validate(
        [_record(high=100.0, low=100.0)],
        batch_id=uuid.uuid4(),
        source="yfinance",
    )

    assert issues == []
