"""Ingestion batch lifecycle management."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import datetime

from src.domain import BatchStatus, IngestionBatch, IngestionRequest


class IngestionBatchManager:
    """Create and update ingestion-batch metadata.

    Preconditions:
        Batch operations refer to `src.domain.IngestionBatch` identities.

    Postconditions:
        Newly created batches start as `PENDING` and retain the request source
        and range. Terminal completion records `COMPLETED` or `FAILED`, sets a
        completion timestamp, and persists all defect/idempotency counters.
    """

    def __init__(self, clock: Callable[[], datetime] = datetime.now) -> None:
        self._clock = clock
        self._batches: dict[uuid.UUID, IngestionBatch] = {}

    def create(self, request: IngestionRequest) -> IngestionBatch:
        """Create a `PENDING` batch for `request`."""
        batch = IngestionBatch(
            source=request.source,
            requested_range=f"{request.start_time.isoformat()}/{request.end_time.isoformat()}",
            ticker_universe=",".join(request.ticker_universe),
            interval=request.interval,
            exchange=request.exchange,
            started_at=self._clock(),
            status=BatchStatus.PENDING,
        )
        self._batches[batch.batch_id] = batch
        return batch

    def mark_completed(self, batch_id: uuid.UUID, status: BatchStatus) -> None:
        """Move a batch to a terminal lifecycle status."""
        batch = self._get_batch(batch_id)
        batch.status = status
        batch.completed_at = self._clock()

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
        """Persist all received, quality-defect, and conflict counters."""
        batch = self._get_batch(batch_id)
        batch.records_received = received
        batch.records_valid = valid
        batch.records_invalid = invalid
        batch.duplicate_count = duplicates
        batch.missing_interval_count = missing_intervals
        batch.stale_response_count = stale_responses
        batch.idempotent_conflict_count = idempotent_conflicts

    def _get_batch(self, batch_id: uuid.UUID) -> IngestionBatch:
        try:
            return self._batches[batch_id]
        except KeyError as exc:
            raise KeyError(f"unknown ingestion batch: {batch_id}") from exc
