"""Detect missing expected time intervals — never silently interpolate."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


class IntervalGapDetector:
    def detect(
        self,
        records: list[dict[str, Any]],
        interval: str,
        expected_start: datetime,
        expected_end: datetime,
        ticker: str,
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        step = self._parse_interval(interval)
        observed = {
            record.get("timestamp")
            for record in records
            if record.get("ticker") == ticker and isinstance(record.get("timestamp"), datetime)
        }

        issues: list[ValidationIssue] = []
        current = expected_start
        while current <= expected_end:
            if current not in observed:
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.MISSING_INTERVAL,
                        severity=IssueSeverity.WARNING,
                        ticker=ticker,
                        timestamp=current,
                        batch_id=batch_id,
                        source=source,
                        details=f"missing expected {interval} bar",
                    )
                )
            current += step

        return issues

    @staticmethod
    def _parse_interval(interval: str) -> timedelta:
        unit = interval[-1]
        value = int(interval[:-1])
        if unit == "m":
            return timedelta(minutes=value)
        if unit == "h":
            return timedelta(hours=value)
        if unit == "d":
            return timedelta(days=value)
        raise ValueError(f"unsupported interval: {interval}")
