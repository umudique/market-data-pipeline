"""Convert accepted timestamps to canonical timezone and representation."""

from __future__ import annotations

from datetime import UTC, datetime


class TimestampNormalizer:
    def __init__(self, canonical_timezone: str) -> None:
        if canonical_timezone != "UTC":
            raise ValueError("only UTC canonical timezone is supported")
        self._canonical_timezone = canonical_timezone

    def normalize(self, raw_timestamp: datetime) -> datetime:
        if raw_timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return raw_timestamp.astimezone(UTC)
