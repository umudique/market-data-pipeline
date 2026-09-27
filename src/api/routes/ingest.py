"""POST /ingest — market-data ingestion trigger."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from src.api.dependencies import (
    build_client_for_request,
    build_ingestion_coordinator,
    get_ingestion_coordinator,
    get_unit_of_work,
)
from src.api.facade import ApplicationServiceFacade
from src.api.schemas import IngestionBatchResponseSchema, IngestionRequestSchema
from src.ingestion.coordinator import IngestionCoordinator
from src.storage.unit_of_work import UnitOfWork

router = APIRouter(tags=["ingestion"])


@router.post("/ingest", response_model=IngestionBatchResponseSchema)
def run_ingestion(
    request: IngestionRequestSchema,
    uow: UnitOfWork = Depends(get_unit_of_work),
    ingestion_coordinator: IngestionCoordinator = Depends(get_ingestion_coordinator),
) -> IngestionBatchResponseSchema:
    """Execute ingestion and embed validation issues in the response."""
    if request.source == "custom":
        ingestion_coordinator = build_ingestion_coordinator(
            uow, build_client_for_request(request.source, request.custom_url, request.api_key)
        )
    facade = ApplicationServiceFacade(
        uow,
        ingestion_coordinator=ingestion_coordinator,
    )
    result = facade.run_ingestion(request)
    # Fetch issues within the same open session — visible after flush, before commit.
    result.validation_issues = facade.list_issues(uuid.UUID(result.batch_id))
    uow.commit()
    return result
