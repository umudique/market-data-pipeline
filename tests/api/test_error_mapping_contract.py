from __future__ import annotations

import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from src.api.errors import not_found_handler, validation_error_handler  # noqa: E402

pytestmark = pytest.mark.unit


def _make_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.add_exception_handler(ValueError, validation_error_handler)
    test_app.add_exception_handler(LookupError, not_found_handler)

    @test_app.get("/raises-value-error")
    def raises_value_error() -> None:
        raise ValueError("invalid screener request")

    @test_app.get("/raises-lookup-error")
    def raises_lookup_error() -> None:
        raise LookupError("batch not found")

    @test_app.get("/raises-runtime-error")
    def raises_runtime_error() -> None:
        raise RuntimeError("database password leaked")

    return test_app


def test_value_error_maps_to_400() -> None:
    client = TestClient(_make_test_app(), raise_server_exceptions=False)
    response = client.get("/raises-value-error")
    assert response.status_code == 400
    assert response.json() == {"detail": "invalid screener request"}


def test_lookup_error_maps_to_404() -> None:
    client = TestClient(_make_test_app(), raise_server_exceptions=False)
    response = client.get("/raises-lookup-error")
    assert response.status_code == 404
    assert response.json() == {"detail": "batch not found"}


def test_unhandled_exception_returns_500_with_safe_body() -> None:
    client = TestClient(_make_test_app(), raise_server_exceptions=False)
    response = client.get("/raises-runtime-error")
    assert response.status_code == 500
    assert "database password leaked" not in response.text
