"""Shared test fixtures."""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Integration fixtures — only active for @pytest.mark.integration tests.
# Requires Docker. Uses testcontainers to spin up a real PostgreSQL instance.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def postgres_url() -> str:
    """Start a PostgreSQL container for the test session and return its URL."""
    pytest.importorskip("testcontainers")
    from testcontainers.community.postgres import PostgresContainer  # type: ignore[import-untyped]

    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url().replace("psycopg2", "psycopg")
