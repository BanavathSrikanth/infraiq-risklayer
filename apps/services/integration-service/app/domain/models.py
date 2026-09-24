from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SourceType(StrEnum):
    csv = "csv"
    json = "json"
    api = "api"
    database = "database"


class PipelineStatus(StrEnum):
    landed = "landed"
    profiled = "profiled"
    mapped = "mapped"
    validated = "validated"
    quarantined = "quarantined"
    normalized = "normalized"


class Source(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    source_key: str
    name: str
    source_type: SourceType
    uri: str | None = None
    enabled: bool = True
    configuration: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class LandingObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    tenant_id: str
    blob_uri: str
    content_type: str
    content_hash: str
    size_bytes: int
    landed_at: datetime = Field(default_factory=utcnow)


class Profile(BaseModel):
    landing_id: str
    columns: list[str]
    row_count: int
    null_counts: dict[str, int] = Field(default_factory=dict)
    inferred_types: dict[str, str] = Field(default_factory=dict)


class Classification(BaseModel):
    source_id: str
    source_type: SourceType
    schema_family: str
    confidence: float = Field(ge=0, le=1)


class MappingSpec(BaseModel):
    source_id: str
    canonical_fields: dict[str, str]
    version: str = "1"


class ValidationIssue(BaseModel):
    row_number: int
    field: str | None = None
    code: str
    message: str


class CanonicalRecord(BaseModel):
    """Only this model may be emitted to downstream scoring or domain services."""

    model_config = ConfigDict(extra="forbid")
    record_id: str
    tenant_id: str
    source_id: str
    observed_at: datetime
    asset_id: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    provenance_id: str


class Provenance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    canonical_record_id: str
    source_id: str
    landing_id: str
    source_row: int
    mapping_version: str
    captured_at: datetime = Field(default_factory=utcnow)
    source_values: dict[str, Any] = Field(default_factory=dict)


class PipelineResult(BaseModel):
    landing: LandingObject
    classification: Classification
    profile: Profile
    status: PipelineStatus
    canonical_records: list[CanonicalRecord] = Field(default_factory=list)
    quarantine: list[ValidationIssue] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
