from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.domain import IssueSeverity, IssueType, ValidationIssue
from src.storage.models import Base
from src.storage.repositories import ValidationIssueRepository

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


def _issue(batch_id: uuid.UUID, ticker: str) -> ValidationIssue:
    return ValidationIssue(
        issue_type=IssueType.INVALID_PRICE,
        severity=IssueSeverity.ERROR,
        ticker=ticker,
        timestamp=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        batch_id=batch_id,
        source="yfinance",
        details="invalid fixture price",
    )


def test_validation_issue_repository_persists_and_filters_by_batch(engine: Engine) -> None:
    target_batch_id = uuid.uuid4()
    other_batch_id = uuid.uuid4()
    target_issues = [_issue(target_batch_id, "AAPL"), _issue(target_batch_id, "MSFT")]
    all_issues = [*target_issues, _issue(other_batch_id, "TSLA")]

    with Session(engine) as session:
        repository = ValidationIssueRepository(session)
        repository.save_all(all_issues)
        session.commit()

        stored = repository.list_by_batch(target_batch_id)

    assert stored == target_issues
    assert all(issue.batch_id == target_batch_id for issue in stored)
