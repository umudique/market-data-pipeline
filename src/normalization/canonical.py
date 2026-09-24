"""Produce final normalized MarketBar and associate source metadata."""

from __future__ import annotations

import uuid
from typing import Any

from src.domain import MarketBar


class RecordCanonicalizer:
    def canonicalize(
        self,
        record: dict[str, Any],
        batch_id: uuid.UUID,
        source: str,
    ) -> MarketBar:
        raise NotImplementedError


class NormalizationResultBuilder:
    def build(
        self,
        bars: list[MarketBar],
        batch_id: uuid.UUID,
    ) -> list[MarketBar]:
        raise NotImplementedError
