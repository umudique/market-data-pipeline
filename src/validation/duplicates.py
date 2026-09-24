"""Detect duplicate candles for the same logical market interval."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


class DuplicateDetector:
    def detect(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        groups: dict[tuple[Any, Any], int] = defaultdict(int)
        for record in records:
            groups[(record.get("ticker"), record.get("timestamp"))] += 1

        return [
            ValidationIssue(
                issue_type=IssueType.DUPLICATE_CANDLE,
                severity=IssueSeverity.ERROR,
                ticker=str(ticker),
                timestamp=timestamp if isinstance(timestamp, datetime) else None,
                batch_id=batch_id,
                source=source,
                details="duplicate candle for ticker/timestamp",
            )
            for (ticker, timestamp), count in groups.items()
            if count > 1
        ]
