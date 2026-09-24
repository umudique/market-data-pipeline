"""Verify and normalise source timestamps into the canonical timezone."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


class TimezoneValidator:
    def __init__(self, canonical_timezone: str) -> None:
        self._canonical_timezone = canonical_timezone

    def validate(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        if self._canonical_timezone != "UTC":
            raise ValueError("only UTC canonical timezone is supported")

        issues: list[ValidationIssue] = []
        for record in records:
            timestamp = record.get("timestamp")
            if isinstance(timestamp, datetime) and timestamp.tzinfo is not None:
                if timestamp.utcoffset() != UTC.utcoffset(timestamp):
                    issues.append(
                        ValidationIssue(
                            issue_type=IssueType.TIMEZONE_NORMALIZATION_REQUIRED,
                            severity=IssueSeverity.WARNING,
                            ticker=str(record.get("ticker", "")),
                            timestamp=timestamp,
                            batch_id=batch_id,
                            source=source,
                            details="timestamp must be normalized to UTC",
                        )
                    )
        return issues
