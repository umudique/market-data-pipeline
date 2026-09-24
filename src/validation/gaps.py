"""Detect missing expected time intervals — never silently interpolate."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.domain import ValidationIssue


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
    ) -> list[ValidationIssue]:
        raise NotImplementedError
