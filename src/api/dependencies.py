"""FastAPI dependency injection — session and service wiring."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from typing import Any, cast

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config import settings
from src.domain import BatchStatus, IngestionBatch, IngestionRequest
from src.ingestion.batches import IngestionBatchManager
from src.ingestion.client import MarketDataClient
from src.ingestion.coordinator import IngestionCoordinator, RetryPolicyProtocol
from src.ingestion.rate_limit import RateLimitController
from src.ingestion.retry import RetryPolicy
from src.ingestion.staleness import StalenessDetector
from src.ingestion.writer import RawRecordWriter
from src.storage.database import get_session
from src.storage.unit_of_work import UnitOfWork
from src.validation.orchestrator import ValidationOrchestrator


class _PersistedBatchManager:
    """Persist batch lifecycle updates while reusing the ingestion batch manager."""

    def __init__(self, manager: IngestionBatchManager, repository: Any) -> None:
        self._manager = manager
        self._repository = repository
        self._batches: dict[uuid.UUID, IngestionBatch] = {}

    def create(self, request: IngestionRequest) -> IngestionBatch:
        batch = self._manager.create(request)
        self._batches[batch.batch_id] = batch
        self._repository.save(batch)
        return batch

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
        self._manager.record_counts(
            batch_id,
            received=received,
            valid=valid,
            invalid=invalid,
            duplicates=duplicates,
            missing_intervals=missing_intervals,
            stale_responses=stale_responses,
            idempotent_conflicts=idempotent_conflicts,
        )
        self._repository.update(self._batches[batch_id])

    def mark_completed(self, batch_id: uuid.UUID, status: BatchStatus) -> None:
        self._manager.mark_completed(batch_id, status)
        self._repository.update(self._batches[batch_id])


def get_db() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


def get_unit_of_work() -> Generator[UnitOfWork, None, None]:
    with UnitOfWork() as uow:
        yield uow


def get_ingestion_coordinator(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> IngestionCoordinator:
    """Assemble the ingestion use case from existing component implementations."""
    return IngestionCoordinator(
        batch_manager=_PersistedBatchManager(IngestionBatchManager(), uow.ingestion_batches),
        rate_limit=RateLimitController(settings.rate_limit_calls_per_minute),
        retry_policy=cast(
            RetryPolicyProtocol,
            RetryPolicy(max_attempts=settings.max_retries, backoff_seconds=0.0),
        ),
        client=MarketDataClient(source="yfinance"),
        staleness_detector=StalenessDetector(),
        raw_writer=RawRecordWriter(uow.raw_market_data),
        validation_handoff=ValidationOrchestrator(),
        issue_store=uow.validation_issues,
    )
