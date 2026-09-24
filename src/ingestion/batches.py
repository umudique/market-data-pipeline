"""Ingestion batch lifecycle management."""

from __future__ import annotations

import uuid

from src.domain import BatchStatus, IngestionBatch, IngestionRequest


class IngestionBatchManager:
    def create(self, request: IngestionRequest) -> IngestionBatch:
        raise NotImplementedError

    def mark_completed(self, batch_id: uuid.UUID, status: BatchStatus) -> None:
        raise NotImplementedError

    def record_counts(
        self,
        batch_id: uuid.UUID,
        *,
        received: int,
        valid: int,
        invalid: int,
        duplicates: int,
        missing_intervals: int,
        stale_responses: int,
        idempotent_conflicts: int,
    ) -> None:
        raise NotImplementedError
