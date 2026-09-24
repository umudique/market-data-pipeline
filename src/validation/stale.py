"""Record stale-response findings as a data-quality condition."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.domain import ValidationIssue


class StaleDataValidator:
    def validate(
        self,
        records: list[dict[str, Any]],
        requested_end: datetime,
        batch_id: uuid.UUID,
        source: str,
    ) -> list[ValidationIssue]:
        raise NotImplementedError
