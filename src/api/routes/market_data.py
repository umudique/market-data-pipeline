"""GET /market-data — normalized validated bars."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/market-data", tags=["market-data"])
