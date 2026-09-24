"""Map provider fields to canonical OHLCV field names."""

from __future__ import annotations

from typing import Any


class SchemaNormalizer:
    def normalize(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
