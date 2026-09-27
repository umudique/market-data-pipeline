"""Record stale-response findings as a data-quality condition."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any, cast

from src.domain import IssueSeverity, IssueType, ValidationIssue


class StaleDataValidator:
    def validate(
        self,
        records: list[dict[str, Any]],
        requested_end: datetime,
        batch_id: uuid.UUID,
        source: str,
        exchange: str | None = None,
        interval: str = "1m",
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
        if _is_daily_or_longer(interval):
            threshold = _last_expected_session(requested_end.date(), exchange)
            if latest_timestamp.date() >= threshold:
                return []
        else:
            if _to_utc(latest_timestamp) >= _to_utc(requested_end):
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


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _is_daily_or_longer(interval: str) -> bool:
    return interval.endswith("d") or interval.endswith("wk") or interval.endswith("mo")


def _last_expected_session(end_date: date, exchange: str | None) -> date:
    if exchange:
        try:
            import exchange_calendars as ec
            import pandas as pd

            cal = ec.get_calendar(exchange)
            return cast(
                date, cal.date_to_session(pd.Timestamp(end_date), direction="previous").date()
            )
        except Exception:
            pass
    d = end_date
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d
