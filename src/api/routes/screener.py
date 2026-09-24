"""POST /screeners/earnings-gap — earnings gap screener endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.dependencies import get_unit_of_work
from src.api.facade import ApplicationServiceFacade
from src.api.schemas import ScreenerRequestSchema, ScreenerResponseSchema

router = APIRouter(prefix="/screeners", tags=["screener"])


@router.post("/earnings-gap", response_model=ScreenerResponseSchema)
def run_earnings_gap_screener(
    request: ScreenerRequestSchema,
    uow: object = Depends(get_unit_of_work),
) -> ScreenerResponseSchema:
    """Execute the earnings-gap screener through the application service facade."""
    return ApplicationServiceFacade(uow).run_earnings_gap(request)
