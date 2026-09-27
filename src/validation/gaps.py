"""Detect missing expected time intervals — never silently interpolate."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from src.domain import IssueSeverity, IssueType, ValidationIssue


def _strip_tz(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None)


def _load_calendar(exchange: str) -> Any:
    import exchange_calendars as ec

    return ec.get_calendar(exchange)


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
        exchange: str | None = None,
    ) -> list[ValidationIssue]:
        step = self._parse_interval(interval)
        tz = expected_start.tzinfo
        naive_start = _strip_tz(expected_start)
        naive_end = _strip_tz(expected_end)
        observed = {
            _strip_tz(record["timestamp"])
            for record in records
            if record.get("ticker") == ticker and isinstance(record.get("timestamp"), datetime)
        }

        cal = None
        if exchange and step == timedelta(days=1):
            try:
                cal = _load_calendar(exchange)
            except Exception:
                pass

        issues: list[ValidationIssue] = []
        current = naive_start
        while current <= naive_end:
            if step == timedelta(days=1):
                if current.weekday() >= 5:
                    current += step
                    continue
                try:
                    if cal is not None and not cal.is_session(current.date()):
                        current += step
                        continue
                except Exception:
                    pass
            if current not in observed:
                issue_ts = current.replace(tzinfo=tz) if tz is not None else current
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.MISSING_INTERVAL,
                        severity=IssueSeverity.WARNING,
                        ticker=ticker,
                        timestamp=issue_ts,
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
