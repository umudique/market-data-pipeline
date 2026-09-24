"""GET /market-data — normalized validated bars."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_unit_of_work
from src.api.facade import ApplicationServiceFacade
from src.api.schemas import MarketDataResponseSchema

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("", response_model=MarketDataResponseSchema)
def get_market_data(
    ticker: str = Query(...),
    start: datetime = Query(...),
    end: datetime = Query(...),
    interval: str = Query("1d"),
    limit: int = Query(100),
    uow: object = Depends(get_unit_of_work),
) -> MarketDataResponseSchema:
    """Return validated normalized market bars for the requested ticker range."""
    return ApplicationServiceFacade(uow).list_market_data(
        ticker=ticker,
        start=start,
        end=end,
        interval=interval,
        limit=limit,
    )
