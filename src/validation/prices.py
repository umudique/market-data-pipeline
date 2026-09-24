"""Detect zero, negative, or structurally invalid OHLC prices."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


class PriceValidator:
    def validate(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for record in records:
            if any(
                self._is_invalid_price(record.get(field))
                for field in ("open", "high", "low", "close")
            ):
                timestamp = record.get("timestamp")
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.INVALID_PRICE,
                        severity=IssueSeverity.ERROR,
                        ticker=str(record.get("ticker", "")),
                        timestamp=timestamp if isinstance(timestamp, datetime) else None,
                        batch_id=batch_id,
                        source=source,
                        details="OHLC prices must be positive",
                    )
                )
        return issues

    @staticmethod
    def _is_invalid_price(value: Any) -> bool:
        return not isinstance(value, int | float) or value <= 0
