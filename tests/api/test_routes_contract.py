from __future__ import annotations

import os
import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from src.api.dependencies import get_ingestion_coordinator, get_unit_of_work  # noqa: E402
from src.api.facade import ApplicationServiceFacade  # noqa: E402
from src.api.main import app  # noqa: E402
from src.api.schemas import IngestionRequestSchema  # noqa: E402
from src.domain import BatchStatus, IngestionBatch, IngestionRequest  # noqa: E402

pytestmark = pytest.mark.unit

_VALID_SCREENER_PAYLOAD = {
    "start_date": "2026-01-02T00:00:00+00:00",
    "end_date": "2026-01-03T00:00:00+00:00",
    "minimum_gap": 5.0,
    "minimum_volume": 1_000_000.0,
    "ticker_universe": ["AAPL"],
}

_VALID_INGESTION_PAYLOAD = {
    "ticker_universe": ["AAPL"],
    "interval": "1d",
    "start_time": "2026-01-02T00:00:00+00:00",
    "end_time": "2026-01-03T00:00:00+00:00",
    "source": "yfinance",
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
def ingestion_coordinator() -> MagicMock:
    coordinator = MagicMock()
    app.dependency_overrides[get_ingestion_coordinator] = lambda: coordinator
    return coordinator


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


def test_ingest_returns_200_with_batch_response_for_valid_request(
    client: TestClient,
    ingestion_coordinator: MagicMock,
) -> None:
    batch_id = uuid.uuid4()
    ingestion_coordinator.run.return_value = IngestionBatch(
        batch_id=batch_id,
        status=BatchStatus.COMPLETED,
        records_received=10,
        records_valid=9,
        records_invalid=1,
        duplicate_count=1,
        missing_interval_count=0,
        stale_response_count=0,
    )

    response = client.post("/ingest", json=_VALID_INGESTION_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["batch_id"] == str(batch_id)
    assert body["status"] == "COMPLETED"
    assert body["records_received"] == 10


def test_ingest_rejects_missing_ticker_universe(client: TestClient) -> None:
    payload = {k: v for k, v in _VALID_INGESTION_PAYLOAD.items() if k != "ticker_universe"}
    response = client.post("/ingest", json=payload)
    assert response.status_code == 422


def test_ingest_rejects_empty_ticker_universe(
    client: TestClient,
    ingestion_coordinator: MagicMock,
) -> None:
    ingestion_coordinator.run.side_effect = ValueError("ticker_universe must not be empty")
    response = client.post("/ingest", json={**_VALID_INGESTION_PAYLOAD, "ticker_universe": []})
    assert response.status_code == 400


def test_ingest_records_batch_status_completed_on_success(
    client: TestClient,
    ingestion_coordinator: MagicMock,
) -> None:
    ingestion_coordinator.run.return_value = IngestionBatch(status=BatchStatus.COMPLETED)

    response = client.post("/ingest", json=_VALID_INGESTION_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_ingest_returns_400_when_coordinator_raises_value_error(
    client: TestClient,
    ingestion_coordinator: MagicMock,
) -> None:
    ingestion_coordinator.run.side_effect = ValueError("invalid ingestion request")

    response = client.post("/ingest", json=_VALID_INGESTION_PAYLOAD)

    assert response.status_code == 400


def test_ingest_facade_delegates_to_coordinator() -> None:
    coordinator = MagicMock()
    coordinator.run.return_value = IngestionBatch(status=BatchStatus.COMPLETED)
    facade = ApplicationServiceFacade(MagicMock(), ingestion_coordinator=coordinator)
    request = IngestionRequestSchema(
        ticker_universe=["AAPL"],
        interval="1d",
        start_time=datetime.fromisoformat("2026-01-02T00:00:00+00:00"),
        end_time=datetime.fromisoformat("2026-01-03T00:00:00+00:00"),
        source="yfinance",
    )

    facade.run_ingestion(request)

    coordinator.run.assert_called_once_with(
        IngestionRequest(
            ticker_universe=["AAPL"],
            interval="1d",
            start_time=request.start_time,
            end_time=request.end_time,
            source="yfinance",
        )
    )
    assert not facade._uow.method_calls
