"""GET /quality/* — ingestion batch summaries and validation issues."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_unit_of_work
from src.api.facade import ApplicationServiceFacade
from src.api.schemas import BatchSummarySchema, ValidationIssueSummarySchema

router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("/batches", response_model=list[BatchSummarySchema])
def list_batches(
    limit: int = Query(20),
    uow: object = Depends(get_unit_of_work),
) -> list[BatchSummarySchema]:
    """Return recent ingestion batch quality summaries."""
    return ApplicationServiceFacade(uow).list_batches(limit)


@router.get("/issues", response_model=list[ValidationIssueSummarySchema])
def list_issues(
    batch_id: uuid.UUID = Query(...),
    uow: object = Depends(get_unit_of_work),
) -> list[ValidationIssueSummarySchema]:
    """Return persisted validation issues for a batch."""
    return ApplicationServiceFacade(uow).list_issues(batch_id)
