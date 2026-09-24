"""Record stale-response findings as a data-quality condition."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


class StaleDataValidator:
    def validate(
        self,
        records: list[dict[str, Any]],
        requested_end: datetime,
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        if not records:
            return []

        timestamps = [
            record["timestamp"]
            for record in records
            if isinstance(record.get("timestamp"), datetime)
        ]
        if not timestamps:
            return []

        latest_timestamp = max(timestamps)
        if latest_timestamp >= requested_end:
            return []

        return [
            ValidationIssue(
                issue_type=IssueType.STALE_RESPONSE,
                severity=IssueSeverity.WARNING,
                ticker=str(records[0].get("ticker", "")),
                timestamp=latest_timestamp,
                batch_id=batch_id,
                source=source,
                details="latest response bar is older than requested end",
            )
        ]
