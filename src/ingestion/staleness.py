"""Stale response detection — HTTP 200 is not automatically valid data."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class StalenessDetector:
    def is_stale(
        self,
        response_bars: list[dict[str, Any]],
        requested_end: datetime,
    ) -> bool:
        raise NotImplementedError
