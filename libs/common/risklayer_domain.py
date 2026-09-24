"""Canonical cross-service domain records.

These records define stable identifiers and boundaries. Service-owned persistence
and application policies remain in the individual services.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProposalStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class DecisionOutcome(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    ACCEPTED = "accepted"
    DEFERRED = "deferred"


class WorkOrderStatus(StrEnum):
    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VerificationResult(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"


class SyncStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCED = "synced"
    PENDING_SYNC = "pending_sync"
    SYNC_FAILED = "sync_failed"


class AssetRegistrationStatus(StrEnum):
    OFFICIAL = "official"
    PROVISIONAL = "provisional"
    REJECTED = "rejected"


class RiskRoutingStatus(StrEnum):
    PROPOSED = "proposed"
    ROUTED = "routed"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class AssignmentStatus(StrEnum):
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REASSIGNED = "reassigned"


@dataclass
class AssetRegistration:
    """A field-discovered asset remains provisional until authorized review."""

    asset_id: str
    tenant_id: str
    registration_status: AssetRegistrationStatus = AssetRegistrationStatus.PROVISIONAL
    discovered_by: str = ""
    discovered_at: datetime = field(default_factory=utc_now)
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    source_observation_id: str | None = None


@dataclass
class RiskRouting:
    routing_id: str
    asset_id: str
    tenant_id: str
    risk_evaluation_id: str
    routed_by: str
    target_team: str
    target_role: str
    status: RiskRoutingStatus = RiskRoutingStatus.PROPOSED
    rationale: str = ""
    automatic_rule_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class WorkAssignment:
    assignment_id: str
    work_order_id: str
    asset_id: str
    tenant_id: str
    assigned_by: str
    assignee_id: str
    assignee_type: str
    status: AssignmentStatus = AssignmentStatus.UNASSIGNED
    territory: str | None = None
    project: str | None = None
    operating_district: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class SyncEnvelope:
    """Idempotent client submission used by offline-capable field devices."""

    client_event_id: str
    device_id: str
    user_id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    operation: str
    payload: dict[str, Any]
    status: SyncStatus = SyncStatus.PENDING_SYNC
    attempt_count: int = 0
    last_error: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    synchronized_at: datetime | None = None


@dataclass
class AccessScope:
    """Additional RBAC scope beyond the user's role."""

    team_ids: list[str] = field(default_factory=list)
    territory_ids: list[str] = field(default_factory=list)
    project_ids: list[str] = field(default_factory=list)
    program_ids: list[str] = field(default_factory=list)
    asset_group_ids: list[str] = field(default_factory=list)
    contractor_id: str | None = None
    operating_district_ids: list[str] = field(default_factory=list)


@dataclass
class DeviceSession:
    user_id: str
    tenant_id: str
    device_id: str
    roles: list[str]
    scope: AccessScope = field(default_factory=AccessScope)
    sync_status: SyncStatus = SyncStatus.ONLINE
    revoked_at: datetime | None = None


@dataclass
class SourceObservation:
    """Immutable source snapshot for any data point that drives a calculation."""

    source_observation_id: str
    tenant_id: str
    source_name: str
    source_type: str
    observed_at: datetime
    captured_at: datetime = field(default_factory=utc_now)
    source_uri: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    source_hash: str | None = None
    version: str = "1.0"


@dataclass
class AssetEvidence:
    evidence_id: str
    tenant_id: str
    asset_id: str
    evidence_type: str
    source_observation_id: str | None = None
    uri: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class RiskDriver:
    risk_driver_id: str
    tenant_id: str
    asset_id: str
    risk_evaluation_id: str
    driver_name: str
    driver_category: str
    contribution_score: float
    explanation: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class HazardExposureRecord:
    exposure_id: str
    tenant_id: str
    asset_id: str
    hazard_type: str
    source_observation_id: str
    geometry_snapshot_id: str | None = None
    score: float = 0.0
    confidence: float = 0.0
    evaluated_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetRelationship:
    relationship_id: str
    tenant_id: str
    source_asset_id: str
    target_asset_id: str
    relationship_type: str
    confidence: float = 1.0
    created_at: datetime = field(default_factory=utc_now)
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass
class RelatedAssetSet:
    set_id: str
    tenant_id: str
    name: str
    asset_ids: list[str] = field(default_factory=list)
    scope_type: str = "spatial"
    created_at: datetime = field(default_factory=utc_now)
    created_by: str = ""


@dataclass
class Condition:
    condition_id: str
    asset_id: str
    tenant_id: str
    condition_type: str
    observed_at: datetime = field(default_factory=utc_now)
    description: str = ""
    measurements: dict[str, Any] = field(default_factory=dict)
    evidence_ids: list[str] = field(default_factory=list)
    source_id: str | None = None


@dataclass
class VegetationCondition:
    vegetation_condition_id: str
    tenant_id: str
    condition_type: str = "vegetation"
    asset_ids: list[str] = field(default_factory=list)
    span_id: str | None = None
    feeder_id: str | None = None
    row_area_id: str | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    clearance_distance_ft: float | None = None
    strike_potential: float | None = None
    growth_rate: float | None = None
    tree_species: str | None = None
    treatment_status: str = "open"
    created_at: datetime = field(default_factory=utc_now)
    created_by: str = ""
    notes: str = ""


@dataclass
class Finding:
    finding_id: str
    asset_id: str
    tenant_id: str
    condition_id: str
    finding_type: str
    description: str
    severity: str = "unknown"
    evidence_ids: list[str] = field(default_factory=list)
    identified_at: datetime = field(default_factory=utc_now)


@dataclass
class Recommendation:
    recommendation_id: str
    asset_id: str
    tenant_id: str
    risk_evaluation_id: str
    recommendation_type: str
    rationale: str
    priority: str
    proposal_status: ProposalStatus = ProposalStatus.PROPOSED
    proposed_by: str = "system"
    approved_by: str | None = None
    reviewed_at: datetime | None = None


@dataclass
class Decision:
    decision_id: str
    asset_id: str
    tenant_id: str
    recommendation_id: str
    outcome: DecisionOutcome
    decided_by: str
    rationale: str = ""
    conditions: list[str] = field(default_factory=list)
    decided_at: datetime = field(default_factory=utc_now)


@dataclass
class WorkOrder:
    work_order_id: str
    asset_id: str
    tenant_id: str
    decision_id: str
    scope: str
    status: WorkOrderStatus = WorkOrderStatus.PLANNED
    assigned_to: str | None = None
    contractor_id: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    estimated_cost: float | None = None
    work_owner_id: str | None = None
    work_owner_type: str | None = None


@dataclass
class Completion:
    completion_id: str
    work_order_id: str
    asset_id: str
    tenant_id: str
    performed_scope: str
    completed_at: datetime = field(default_factory=utc_now)
    evidence_ids: list[str] = field(default_factory=list)
    actual_cost: float | None = None
    submitted_by: str = ""


@dataclass
class Verification:
    verification_id: str
    work_order_id: str
    asset_id: str
    tenant_id: str
    result: VerificationResult
    verified_by: str
    criteria: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    verified_at: datetime = field(default_factory=utc_now)
    notes: str = ""
    performer_id: str | None = None


@dataclass
class ResidualRisk:
    residual_risk_id: str
    asset_id: str
    tenant_id: str
    prior_risk_evaluation_id: str
    post_treatment_risk_evaluation_id: str
    risk_score: float
    accepted_by: str | None = None
    monitoring_required: bool = True
    evaluated_at: datetime = field(default_factory=utc_now)


@dataclass
class AIProposal:
    proposal_id: str = field(default_factory=lambda: str(uuid4()))
    asset_id: str = ""
    tenant_id: str = ""
    target_type: str = ""
    target_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    proposal_status: ProposalStatus = ProposalStatus.PROPOSED
    authoritative: bool = False
    provider: str = ""
    model: str = ""
    prompt_id: str = ""
    generated_at: datetime = field(default_factory=utc_now)
