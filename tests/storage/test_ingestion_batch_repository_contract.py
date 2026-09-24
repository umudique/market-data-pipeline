from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.domain import BatchStatus, IngestionBatch
from src.storage.models import Base
from src.storage.repositories import IngestionBatchRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def engine(postgres_url: str) -> Iterator[Engine]:
    db_engine = create_engine(postgres_url)
    Base.metadata.create_all(db_engine)
    try:
        yield db_engine
    finally:
        Base.metadata.drop_all(db_engine)
        db_engine.dispose()


def _batch() -> IngestionBatch:
    return IngestionBatch(
        batch_id=uuid.uuid4(),
        source="yfinance",
        requested_range="2026-01-02T14:30:00+00:00/2026-01-02T14:31:00+00:00",
        started_at=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        status=BatchStatus.PENDING,
    )


def test_ingestion_batch_repository_saves_and_updates_batch(engine: Engine) -> None:
    batch = _batch()

    with Session(engine) as session:
        repository = IngestionBatchRepository(session)
        repository.save(batch)
        session.commit()

        saved = repository.get_by_id(batch.batch_id)
        assert saved == batch

        batch.status = BatchStatus.COMPLETED
        batch.completed_at = datetime(2026, 1, 2, 14, 32, tzinfo=UTC)
        batch.records_received = 2
        batch.records_valid = 2
        batch.idempotent_conflict_count = 1
        repository.update(batch)
        session.commit()

        updated = repository.get_by_id(batch.batch_id)

    assert updated == batch
    assert updated is not None
    assert updated.status is BatchStatus.COMPLETED
    assert updated.records_received == 2
    assert updated.idempotent_conflict_count == 1
