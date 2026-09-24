"""Engine and session factory."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings

engine = create_engine(settings.database_url)
SessionFactory: type[Session] = sessionmaker(bind=engine)  # type: ignore[assignment]


def get_session() -> Session:
    return SessionFactory()
