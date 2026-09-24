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
        raise NotImplementedError

    def create(self, request: IngestionRequest) -> IngestionBatch:
        """Create a `PENDING` batch for `request`."""
        raise NotImplementedError

    def mark_completed(self, batch_id: uuid.UUID, status: BatchStatus) -> None:
        """Move a batch to a terminal lifecycle status."""
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
        """Persist all received, quality-defect, and conflict counters."""
        raise NotImplementedError
