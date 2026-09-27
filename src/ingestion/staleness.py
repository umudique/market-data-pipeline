"""Stale response detection — HTTP 200 is not automatically valid data."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any, cast


class StalenessDetector:
    """Detect stale provider responses before they are accepted.

    Preconditions:
        `response_bars` are parsed source-record dictionaries that include a
        comparable bar timestamp. `requested_end` is the expected freshness
        boundary for the request.

    Postconditions:
        Returns `True` when the latest response timestamp is older than the
        requested freshness boundary. A stale response is never silently
        accepted; callers must record the condition in batch/validation
        metadata.
    """

    def is_stale(
        self,
        response_bars: list[dict[str, Any]],
        requested_end: datetime,
        interval: str = "1m",
        exchange: str | None = None,
    ) -> bool:
        """Return whether the response is older than `requested_end`."""
        if not response_bars:
            return True

        latest_timestamp = max(bar["timestamp"] for bar in response_bars)
        if not isinstance(latest_timestamp, datetime):
            raise TypeError("response bar timestamp must be a datetime")

        if _is_daily_or_longer(interval):
            threshold = _last_expected_session(requested_end.date(), exchange)
            return latest_timestamp.date() < threshold

        return _to_utc(latest_timestamp) < _to_utc(requested_end)


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


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
