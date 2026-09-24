"""Detect malformed, impossible, or inconsistent timestamps."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


class TimestampValidator:
    def validate(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for record in records:
            timestamp = record.get("timestamp")
            if not isinstance(timestamp, datetime) or timestamp.tzinfo is None:
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.INVALID_TIMESTAMP,
                        severity=IssueSeverity.ERROR,
                        ticker=str(record.get("ticker", "")),
                        timestamp=timestamp if isinstance(timestamp, datetime) else None,
                        batch_id=batch_id,
                        source=source,
                        details="timestamp must be timezone-aware",
                    )
                )
        return issues
