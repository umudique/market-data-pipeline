"""Detect missing required OHLCV observations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


class ObservationValidator:
    _required_fields = ("open", "high", "low", "close", "volume")

    def validate(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for record in records:
            if any(field not in record or record[field] is None for field in self._required_fields):
                timestamp = record.get("timestamp")
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.MISSING_OBSERVATION,
                        severity=IssueSeverity.ERROR,
                        ticker=str(record.get("ticker", "")),
                        timestamp=timestamp if isinstance(timestamp, datetime) else None,
                        batch_id=batch_id,
                        source=source,
                        details="required OHLCV observation missing",
                    )
                )
        return issues
