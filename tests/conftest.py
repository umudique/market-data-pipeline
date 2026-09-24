"""Shared test fixtures."""

from __future__ import annotations

import os
import pathlib

import pytest


def pytest_configure(config: pytest.Config) -> None:
    # Rootless Podman: point testcontainers at the user Podman socket when
    # DOCKER_HOST is not already set (e.g. in CI with a real Docker daemon).
    podman_socket = pathlib.Path(f"/run/user/{os.getuid()}/podman/podman.sock")
    if podman_socket.exists() and "DOCKER_HOST" not in os.environ:
        os.environ["DOCKER_HOST"] = f"unix://{podman_socket}"
    # Ryuk reaper does not work with rootless Podman.
    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")


# ---------------------------------------------------------------------------
# Integration fixtures — only active for @pytest.mark.integration tests.
# Requires Docker/Podman. Uses testcontainers to spin up a real PostgreSQL.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def postgres_url() -> str:
    """Start a PostgreSQL container for the test session and return its URL."""
    pytest.importorskip("testcontainers")
    from testcontainers.community.postgres import PostgresContainer  # type: ignore[import-untyped]

    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url().replace("psycopg2", "psycopg")
