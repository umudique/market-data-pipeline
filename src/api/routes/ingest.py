"""POST /ingest — market-data ingestion trigger."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.dependencies import get_ingestion_coordinator, get_unit_of_work
from src.api.facade import ApplicationServiceFacade
from src.api.schemas import IngestionBatchResponseSchema, IngestionRequestSchema
from src.ingestion.coordinator import IngestionCoordinator

router = APIRouter(tags=["ingestion"])


@router.post("/ingest", response_model=IngestionBatchResponseSchema)
def run_ingestion(
    request: IngestionRequestSchema,
    uow: object = Depends(get_unit_of_work),
    coordinator: IngestionCoordinator = Depends(get_ingestion_coordinator),
) -> IngestionBatchResponseSchema:
    """Execute ingestion through the application service facade."""
    return ApplicationServiceFacade(uow, ingestion_coordinator=coordinator).run_ingestion(request)
