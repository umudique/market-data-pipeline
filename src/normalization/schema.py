"""Map provider fields to canonical OHLCV field names."""

from __future__ import annotations

from typing import Any


class SchemaNormalizer:
    _canonical_keys = ("ticker", "timestamp", "open", "high", "low", "close", "volume")

    def normalize(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {key: raw_record[key] for key in self._canonical_keys if key in raw_record}
