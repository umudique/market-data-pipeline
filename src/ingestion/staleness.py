"""Stale response detection — HTTP 200 is not automatically valid data."""

from __future__ import annotations

from datetime import datetime
from typing import Any


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
    ) -> bool:
        """Return whether the response is older than `requested_end`."""
        if not response_bars:
            return True

        latest_timestamp = max(bar["timestamp"] for bar in response_bars)
        if not isinstance(latest_timestamp, datetime):
            raise TypeError("response bar timestamp must be a datetime")

        return latest_timestamp < requested_end
