"""Produce final normalized MarketBar and associate source metadata."""

from __future__ import annotations

import uuid
from typing import Any

from src.domain import MarketBar, ValidationStatus


class RecordCanonicalizer:
    def canonicalize(
        self,
        record: dict[str, Any],
        batch_id: uuid.UUID,
        source: str,
    ) -> MarketBar:
        return MarketBar(
            ticker=str(record["ticker"]),
            timestamp=record["timestamp"],
            interval=str(record["interval"]),
            open=float(record["open"]),
            high=float(record["high"]),
            low=float(record["low"]),
            close=float(record["close"]),
            volume=float(record["volume"]),
            source=source,
            ingestion_batch_id=batch_id,
            validated=True,
            validation_status=ValidationStatus.VALID,
        )


class NormalizationResultBuilder:
    def build(
        self,
        bars: list[MarketBar],
        batch_id: uuid.UUID,
    ) -> list[MarketBar]:
        return bars
