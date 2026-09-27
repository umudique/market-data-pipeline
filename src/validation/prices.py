"""Detect zero, negative, or structurally invalid OHLC prices."""

from __future__ import annotations

import math
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
            timestamp = record.get("timestamp")
            ts = timestamp if isinstance(timestamp, datetime) else None
            ticker = str(record.get("ticker", ""))

            if any(
                self._is_invalid_price(record.get(field))
                for field in ("open", "high", "low", "close")
            ):
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.INVALID_PRICE,
                        severity=IssueSeverity.ERROR,
                        ticker=ticker,
                        timestamp=ts,
                        batch_id=batch_id,
                        source=source,
                        details="OHLC prices must be finite and positive",
                    )
                )
                continue

            try:
                if float(record["high"]) < float(record["low"]):
                    issues.append(
                        ValidationIssue(
                            issue_type=IssueType.OHLC_INCONSISTENCY,
                            severity=IssueSeverity.ERROR,
                            ticker=ticker,
                            timestamp=ts,
                            batch_id=batch_id,
                            source=source,
                            details=f"high {record['high']} < low {record['low']}",
                        )
                    )
            except (KeyError, TypeError, ValueError):
                pass

        return issues

    @staticmethod
    def _is_invalid_price(value: Any) -> bool:
        if not isinstance(value, int | float):
            return True
        return not math.isfinite(value) or value <= 0
