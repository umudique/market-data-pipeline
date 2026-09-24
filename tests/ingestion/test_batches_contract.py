from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.domain import BatchStatus, IngestionRequest
from src.ingestion.batches import IngestionBatchManager

pytestmark = pytest.mark.unit


def _request() -> IngestionRequest:
    return IngestionRequest(
        ticker_universe=["AAPL"],
        interval="1m",
        start_time=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        end_time=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
        source="yfinance",
    )


def test_ingestion_batch_lifecycle_pending_to_completed() -> None:
    manager = IngestionBatchManager(clock=lambda: datetime(2026, 1, 2, 14, 33, tzinfo=UTC))

    batch = manager.create(_request())
    assert batch.status is BatchStatus.PENDING
    assert batch.source == "yfinance"
    assert batch.requested_range == "2026-01-02T14:30:00+00:00/2026-01-02T14:32:00+00:00"

    manager.record_counts(
        batch.batch_id,
        received=2,
        valid=2,
        invalid=0,
        duplicates=0,
        missing_intervals=0,
        stale_responses=0,
        idempotent_conflicts=0,
    )
    manager.mark_completed(batch.batch_id, BatchStatus.COMPLETED)

    assert batch.status is BatchStatus.COMPLETED
    assert batch.completed_at == datetime(2026, 1, 2, 14, 33, tzinfo=UTC)
    assert batch.records_received == 2
    assert batch.records_valid == 2


def test_ingestion_batch_lifecycle_pending_to_failed() -> None:
    manager = IngestionBatchManager(clock=lambda: datetime(2026, 1, 2, 14, 33, tzinfo=UTC))

    batch = manager.create(_request())
    manager.record_counts(
        batch.batch_id,
        received=0,
        valid=0,
        invalid=0,
        duplicates=0,
        missing_intervals=0,
        stale_responses=0,
        idempotent_conflicts=0,
    )
    manager.mark_completed(batch.batch_id, BatchStatus.FAILED)

    assert batch.status is BatchStatus.FAILED
    assert batch.completed_at == datetime(2026, 1, 2, 14, 33, tzinfo=UTC)


def test_idempotent_conflict_count_is_recorded_for_reingested_range() -> None:
    manager = IngestionBatchManager(clock=lambda: datetime(2026, 1, 2, 14, 33, tzinfo=UTC))

    batch = manager.create(_request())
    manager.record_counts(
        batch.batch_id,
        received=2,
        valid=2,
        invalid=0,
        duplicates=0,
        missing_intervals=0,
        stale_responses=0,
        idempotent_conflicts=2,
    )
    manager.mark_completed(batch.batch_id, BatchStatus.COMPLETED)

    assert batch.idempotent_conflict_count == 2
    assert batch.status is BatchStatus.COMPLETED
