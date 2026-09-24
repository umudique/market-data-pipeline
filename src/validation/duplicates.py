"""Detect duplicate candles for the same logical market interval."""

from __future__ import annotations

import uuid
from typing import Any

from src.domain import ValidationIssue


class DuplicateDetector:
    def detect(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        raise NotImplementedError
