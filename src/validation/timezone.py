"""Verify and normalise source timestamps into the canonical timezone."""

from __future__ import annotations

import uuid
from typing import Any

from src.domain import ValidationIssue


class TimezoneValidator:
    def __init__(self, canonical_timezone: str) -> None:
        raise NotImplementedError

    def validate(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        raise NotImplementedError
