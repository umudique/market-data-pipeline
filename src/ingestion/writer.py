"""Raw source-payload persistence at the raw/staging boundary."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

from src.domain import IngestionBatch


class RawDataRepositoryProtocol(Protocol):
    def save_raw(
        self,
        batch_id: uuid.UUID,
        source: str,
        ticker: str,
        payload: str,
    ) -> None: ...


@dataclass
class RawRecordWriter:
    """Persist source payloads to the raw/staging boundary.

    Preconditions:
        Records are provider/source dictionaries associated with an ingestion
        batch. They may contain defects and are not trusted.

    Postconditions:
        When `repository` is provided, each record is durably persisted via
        `RawMarketDataRepository`. Without a repository (tests / in-process
        staging), payloads are kept in `staged_records` for auditability.
        This component never writes to trusted `market_bars`.
    """

    repository: RawDataRepositoryProtocol | None = None
    staged_records: list[tuple[IngestionBatch, list[dict[str, Any]]]] = field(default_factory=list)

    def write_batch(
        self,
        batch: IngestionBatch,
        records: list[dict[str, Any]],
    ) -> int:
        """Persist raw records for `batch` and return the staged count."""
        if self.repository is not None:
            for record in records:
                self.repository.save_raw(
                    batch.batch_id,
                    batch.source,
                    str(record.get("ticker", "")),
                    str(record.get("raw_payload", "")),
                )
        else:
            self.staged_records.append((batch, records))
        return len(records)
