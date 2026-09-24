from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    source_id: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    locator: str | None = None
    excerpt: str | None = None


class ProvenanceMetadata(BaseModel):
    model_provider: str
    model_name: str
    model_version: str
    prompt_id: str
    prompt_version: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_references: list[SourceReference] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    authoritative: Literal[False] = False
    proposal_status: Literal["proposed"] = "proposed"


class EntityProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    entity_type: str
    attributes: dict[str, Any]
    provenance: ProvenanceMetadata


class RelationshipProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    relationship_type: str
    source_entity: str
    target_entity: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    provenance: ProvenanceMetadata


class RecommendationProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    recommendation_type: str
    rationale: str
    priority: Literal["low", "medium", "high", "critical"]
    provenance: ProvenanceMetadata


class AIProposalResponse(BaseModel):
    operation: str
    entities: list[EntityProposal] = Field(default_factory=list)
    relationships: list[RelationshipProposal] = Field(default_factory=list)
    recommendations: list[RecommendationProposal] = Field(default_factory=list)
    authoritative_record_ids: list[str] = Field(default_factory=list)
    note: str = (
        "AI output is a proposal. Application/domain services must validate and "
        "persist authoritative business records."
    )
