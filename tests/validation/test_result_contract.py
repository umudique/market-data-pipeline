from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.domain import IssueSeverity, IssueType, ValidationIssue, ValidationStatus
from src.validation.result import ValidationResultAggregator

pytestmark = pytest.mark.unit


def _issue(severity: IssueSeverity) -> ValidationIssue:
    return ValidationIssue(
        issue_type=(
            IssueType.INVALID_PRICE
            if severity is IssueSeverity.ERROR
            else IssueType.MISSING_INTERVAL
        ),
        severity=severity,
        ticker="AAPL",
        timestamp=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        batch_id=uuid.uuid4(),
        source="yfinance",
    )


def test_validation_result_aggregator_marks_zero_issues_valid() -> None:
    result = ValidationResultAggregator().aggregate([])

    assert result.status is ValidationStatus.VALID
    assert result.issues == []


def test_validation_result_aggregator_marks_any_error_invalid() -> None:
    error_issue = _issue(IssueSeverity.ERROR)
    warning_issue = _issue(IssueSeverity.WARNING)

    result = ValidationResultAggregator().aggregate([warning_issue, error_issue])

    assert result.status is ValidationStatus.INVALID
    assert result.issues == [warning_issue, error_issue]


def test_validation_result_aggregator_marks_only_warnings_flagged() -> None:
    warning_issue = _issue(IssueSeverity.WARNING)

    result = ValidationResultAggregator().aggregate([warning_issue])

    assert result.status is ValidationStatus.FLAGGED
    assert result.issues == [warning_issue]
