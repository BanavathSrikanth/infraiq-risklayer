"""Typed, row-oriented ingestion of risk input CSV files.

CSV headers use the RiskInput field paths (for example ``ahs.age_years`` and
``weather.wind_speed_mph``). List-valued fields may contain JSON. Invalid rows
are reported independently and do not prevent valid rows in the same batch
from being calculated and persisted.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from app.application.risk_calculation import RiskCalculationService
from app.domain.schemas.risk_input import RiskInput


@dataclass
class RowError:
    row: int
    errors: list[dict[str, Any]]


@dataclass
class IngestionResult:
    blob_name: str
    records_received: int
    records_processed: int
    results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[RowError] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "blob_name": self.blob_name,
            "records_received": self.records_received,
            "records_processed": self.records_processed,
            "results": self.results,
            "errors": [
                {"row": error.row, "errors": error.errors}
                for error in self.errors
            ],
        }


class RiskCsvIngestionService:
    def __init__(
        self,
        risk_service: RiskCalculationService,
        repository: Any,
    ) -> None:
        self.risk_service = risk_service
        self.repository = repository

    @staticmethod
    def _value(value: str) -> Any:
        value = value.strip()
        if not value:
            return None
        if value.startswith("{") or value.startswith("["):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    @classmethod
    def _row_payload(cls, row: dict[str, str]) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for key, raw_value in row.items():
            if not key or key is None:
                continue
            value = cls._value(raw_value or "")
            if value is None:
                continue
            target = payload
            parts = key.strip().split(".")
            for part in parts[:-1]:
                target = target.setdefault(part, {})
            target[parts[-1]] = value
        return payload

    def ingest(
        self,
        content: bytes,
        blob_name: str,
        tenant_id: str | None = None,
    ) -> IngestionResult:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("CSV blob must be UTF-8 encoded") from exc

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise ValueError("CSV blob must include a header row")

        output = IngestionResult(blob_name, 0, 0)
        for row_number, row in enumerate(reader, start=2):
            output.records_received += 1
            try:
                risk_input = RiskInput.model_validate(self._row_payload(row))
                if tenant_id and risk_input.tenant_id != tenant_id:
                    raise ValueError(
                        f"tenant_id does not match requested tenant '{tenant_id}'"
                    )
                result = self.risk_service.calculate(risk_input)
                persisted = self.repository.append(result)
                output.results.append(persisted.model_dump(mode="json"))
                output.records_processed += 1
            except ValidationError as exc:
                output.errors.append(
                    RowError(row_number, exc.errors(include_url=False))
                )
            except (KeyError, TypeError, ValueError) as exc:
                output.errors.append(
                    RowError(row_number, [{"loc": [], "msg": str(exc)}])
                )
        return output
