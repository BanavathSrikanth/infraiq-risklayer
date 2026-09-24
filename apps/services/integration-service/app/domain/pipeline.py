from __future__ import annotations

import csv
import io
import json
from hashlib import sha256
from typing import Any
from uuid import uuid4

from app.domain.models import (
    CanonicalRecord,
    Classification,
    LandingObject,
    MappingSpec,
    PipelineResult,
    PipelineStatus,
    Profile,
    Provenance,
    Source,
    ValidationIssue,
)
from app.infrastructure.blob import BlobLandingAdapter
from app.infrastructure.repository import IntegrationRepository


class IntegrationPipeline:
    def __init__(self, repository: IntegrationRepository, blob: BlobLandingAdapter) -> None:
        self.repository, self.blob = repository, blob

    def ingest(
        self, source: Source, data: bytes, content_type: str, mapping: MappingSpec
    ) -> PipelineResult:
        landed_blob = self.blob.land(source.id, data, content_type)
        classification = Classification(
            source_id=source.id,
            source_type=source.source_type,
            schema_family=source.configuration.get("schema_family", "generic"),
            confidence=1.0 if source.source_type.value in content_type else 0.8,
        )
        landing = LandingObject(
            source_id=source.id,
            tenant_id=source.tenant_id,
            blob_uri=landed_blob.uri,
            content_type=content_type,
            content_hash=sha256(data).hexdigest(),
            size_bytes=len(data),
        )
        self.repository.save(landing)
        rows = self._parse(data, content_type)
        columns = sorted({key for row in rows for key in row})
        profile = Profile(
            landing_id=landing.id,
            columns=columns,
            row_count=len(rows),
            null_counts={c: sum(row.get(c) in (None, "") for row in rows) for c in columns},
            inferred_types={c: self._infer_type(rows, c) for c in columns},
        )
        self.repository.save_profile(profile)
        self.repository.save_mapping(mapping)
        canonical, issues, provenance = [], [], []
        for number, row in enumerate(rows, 1):
            mapped = {target: row.get(source_field) for target, source_field in mapping.canonical_fields.items()}
            missing = [field for field in ("asset_id", "observed_at") if not mapped.get(field)]
            if missing:
                issues.extend(
                    ValidationIssue(row_number=number, field=field, code="required", message=f"{field} is required")
                    for field in missing
                )
                continue
            try:
                record = CanonicalRecord(
                    record_id=str(uuid4()),
                    tenant_id=source.tenant_id,
                    source_id=source.id,
                    observed_at=mapped["observed_at"],
                    asset_id=str(mapped["asset_id"]),
                    attributes={k: v for k, v in mapped.items() if k not in {"asset_id", "observed_at"}},
                    provenance_id=str(uuid4()),
                )
            except Exception as exc:
                issues.append(ValidationIssue(row_number=number, code="invalid", message=str(exc)))
                continue
            self.repository.save_canonical(record)
            prov = Provenance(
                id=record.provenance_id,
                canonical_record_id=record.record_id,
                source_id=source.id,
                landing_id=landing.id,
                source_row=number,
                mapping_version=mapping.version,
                source_values=dict(row),
            )
            self.repository.save_provenance(prov)
            canonical.append(record)
            provenance.append(prov)
        status = PipelineStatus.normalized if canonical and not issues else PipelineStatus.quarantined
        return PipelineResult(
            landing=landing, classification=classification, profile=profile, status=status,
            canonical_records=canonical, quarantine=issues, provenance=provenance,
        )

    @staticmethod
    def _parse(data: bytes, content_type: str) -> list[dict[str, Any]]:
        text = data.decode("utf-8-sig")
        if "json" in content_type:
            payload = json.loads(text)
            return payload if isinstance(payload, list) else [payload]
        return list(csv.DictReader(io.StringIO(text)))

    @staticmethod
    def _infer_type(rows: list[dict[str, Any]], column: str) -> str:
        values = [row.get(column) for row in rows if row.get(column) not in (None, "")]
        if not values:
            return "null"
        if all(str(v).lower() in {"true", "false"} for v in values):
            return "boolean"
        try:
            [float(v) for v in values]
            return "number"
        except (TypeError, ValueError):
            return "string"
