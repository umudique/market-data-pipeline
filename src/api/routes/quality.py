"""GET /quality/* — ingestion batch summaries and validation issues."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/quality", tags=["quality"])
