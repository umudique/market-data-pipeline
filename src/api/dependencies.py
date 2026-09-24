"""FastAPI dependency injection — session and service wiring."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from src.storage.database import get_session
from src.storage.unit_of_work import UnitOfWork


def get_db() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


def get_unit_of_work() -> Generator[UnitOfWork, None, None]:
    with UnitOfWork() as uow:
        yield uow
