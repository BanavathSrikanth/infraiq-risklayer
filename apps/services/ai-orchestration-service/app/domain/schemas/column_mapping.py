from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    name: str
    inferred_type: Literal["string", "integer", "number", "boolean", "date", "empty", "unknown"]
    nullable: bool
    sample_values: list[str] = Field(default_factory=list)
    null_fraction: float = Field(ge=0, le=1)


class MappingItem(BaseModel):
    source_column: str
    target_field: str | None = None
    confidence: float = Field(ge=0, le=1)
    transformation: str | None = None
    reason: str


class MappingProposal(BaseModel):
    mappings: list[MappingItem] = Field(default_factory=list)
    unmapped_columns: list[str] = Field(default_factory=list)
    requires_review: bool = False


class MappingRecord(BaseModel):
    mapping_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    source_uri: str
    schema_name: str
    columns: list[ColumnProfile]
    proposal: MappingProposal
    status: Literal["proposed", "approved", "rejected"] = "proposed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None


class CreateMappingRequest(BaseModel):
    tenant_id: str
    schema_name: str
    source_uri: str = Field(description="Blob URI or local file path in development")
    target_fields: list[str] = Field(min_length=1)


class ReviewMappingRequest(BaseModel):
    reviewer: str
    decision: Literal["approved", "rejected"]
    mappings: list[MappingItem] | None = None