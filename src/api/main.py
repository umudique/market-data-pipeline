"""FastAPI application — thin delivery layer, no business logic here."""

from __future__ import annotations

from fastapi import FastAPI

from src.api.errors import not_found_handler, validation_error_handler
from src.api.routes import market_data, quality, screener

app = FastAPI(title="Market Data Pipeline", version="0.1.0")

app.add_exception_handler(ValueError, validation_error_handler)
app.add_exception_handler(LookupError, not_found_handler)

app.include_router(market_data.router)
app.include_router(screener.router)
app.include_router(quality.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
