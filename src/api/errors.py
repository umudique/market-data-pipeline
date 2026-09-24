"""Map domain and infrastructure errors to consistent HTTP responses."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
