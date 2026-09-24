from __future__ import annotations

import os
import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from src.api.dependencies import get_unit_of_work  # noqa: E402
from src.api.main import app  # noqa: E402

pytestmark = pytest.mark.unit

_VALID_SCREENER_PAYLOAD = {
    "start_date": "2026-01-02T00:00:00+00:00",
    "end_date": "2026-01-03T00:00:00+00:00",
    "minimum_gap": 5.0,
    "minimum_volume": 1_000_000.0,
    "ticker_universe": ["AAPL"],
}


@pytest.fixture(autouse=True)
def override_uow() -> MagicMock:
    mock = MagicMock()
    mock.market_bars.list_by_ticker.return_value = []
    mock.ingestion_batches.list_recent.return_value = []
    mock.validation_issues.list_by_batch.return_value = []
    mock.screener.earnings_gap_candidates.return_value = []
    app.dependency_overrides[get_unit_of_work] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_screener_returns_200_for_valid_request(client: TestClient) -> None:
    response = client.post("/screeners/earnings-gap", json=_VALID_SCREENER_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert "total" in body


def test_screener_rejects_missing_ticker_universe(client: TestClient) -> None:
    payload = {k: v for k, v in _VALID_SCREENER_PAYLOAD.items() if k != "ticker_universe"}
    response = client.post("/screeners/earnings-gap", json=payload)
    assert response.status_code == 422


def test_market_data_returns_200_for_valid_request(client: TestClient) -> None:
    response = client.get(
        "/market-data",
        params={
            "ticker": "AAPL",
            "start": "2026-01-02T00:00:00+00:00",
            "end": "2026-01-03T00:00:00+00:00",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "bars" in body
    assert "total" in body


def test_market_data_rejects_missing_ticker(client: TestClient) -> None:
    response = client.get(
        "/market-data",
        params={
            "start": "2026-01-02T00:00:00+00:00",
            "end": "2026-01-03T00:00:00+00:00",
        },
    )
    assert response.status_code == 422


def test_quality_batches_returns_200(client: TestClient) -> None:
    response = client.get("/quality/batches")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_quality_issues_returns_200_for_valid_batch_id(client: TestClient) -> None:
    response = client.get("/quality/issues", params={"batch_id": str(uuid.uuid4())})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_quality_issues_rejects_missing_batch_id(client: TestClient) -> None:
    response = client.get("/quality/issues")
    assert response.status_code == 422
