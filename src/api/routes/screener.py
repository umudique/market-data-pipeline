"""POST /screeners/earnings-gap — earnings gap screener endpoint."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/screeners", tags=["screener"])
