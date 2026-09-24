"""Map domain and infrastructure errors to consistent HTTP responses."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


async def validation_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    raise NotImplementedError


async def not_found_handler(request: Request, exc: LookupError) -> JSONResponse:
    raise NotImplementedError
