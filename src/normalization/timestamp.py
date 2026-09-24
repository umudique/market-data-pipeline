"""Convert accepted timestamps to canonical timezone and representation."""

from __future__ import annotations

from datetime import datetime


class TimestampNormalizer:
    def __init__(self, canonical_timezone: str) -> None:
        raise NotImplementedError

    def normalize(self, raw_timestamp: datetime) -> datetime:
        raise NotImplementedError
