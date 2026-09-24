"""Detect zero, negative, or structurally invalid OHLC prices."""

from __future__ import annotations

import uuid
from typing import Any

from src.domain import ValidationIssue


class PriceValidator:
    def validate(
        self,
        records: list[dict[str, Any]],
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        raise NotImplementedError
