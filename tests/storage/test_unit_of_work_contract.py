from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import sessionmaker

from src.domain import MarketBar, ValidationStatus
from src.storage.models import Base, MarketBarModel
from src.storage.unit_of_work import UnitOfWork

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


def _uow(engine: Engine) -> UnitOfWork:
    uow = UnitOfWork()
    uow.session_factory = sessionmaker(bind=engine)
    return uow


def _bar() -> MarketBar:
    return MarketBar(
        ticker="AAPL",
        timestamp=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        interval="1m",
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        volume=1200.0,
        source="yfinance",
        ingestion_batch_id=uuid.uuid4(),
        validated=True,
        validation_status=ValidationStatus.VALID,
    )


def test_unit_of_work_commits_successful_block(engine: Engine) -> None:
    with _uow(engine) as uow:
        uow.market_bars.upsert_all([_bar()])

    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:
        rows = session.scalars(select(MarketBarModel)).all()

    assert len(rows) == 1
    assert rows[0].ticker == "AAPL"


def test_unit_of_work_rolls_back_failed_block(engine: Engine) -> None:
    with pytest.raises(RuntimeError):
        with _uow(engine) as uow:
            uow.market_bars.upsert_all([_bar()])
            raise RuntimeError("force rollback")

    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:
        rows = session.scalars(select(MarketBarModel)).all()

    assert rows == []
