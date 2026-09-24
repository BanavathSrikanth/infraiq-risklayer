"""Canonical geospatial contracts shared by map, ingestion, and risk services."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


HazardType = Literal["heat", "flood", "wind", "fire", "vegetation", "other"]
GeometryType = Literal["Point", "Polygon", "MultiPolygon"]


@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float
    coordinate_reference_system: str = "EPSG:4326"


@dataclass(frozen=True)
class AssetLocationSnapshot:
    location_id: str
    asset_id: str
    tenant_id: str
    point: GeoPoint
    source: str
    observed_at: datetime
    recorded_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class HazardLayerSnapshot:
    layer_snapshot_id: str
    tenant_id: str
    hazard_type: HazardType
    source: str
    source_uri: str
    source_observed_at: datetime
    ingested_at: datetime
    valid_from: datetime | None
    valid_to: datetime | None
    geometry: dict[str, Any]
    properties: dict[str, Any] = field(default_factory=dict)
    source_event_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class AssetHazardExposure:
    exposure_id: str
    asset_id: str
    tenant_id: str
    layer_snapshot_id: str
    hazard_type: HazardType
    exposure_score: float
    intersection_type: Literal["inside", "intersects", "nearest", "none"]
    evaluated_at: datetime = field(default_factory=utc_now)
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolePriorityEvaluation:
    priority_evaluation_id: str
    asset_id: str
    tenant_id: str
    risk_evaluation_id: str
    priority_score: float
    priority_band: Literal["low", "medium", "high", "critical"]
    factors: dict[str, float]
    evaluated_at: datetime = field(default_factory=utc_now)
    rule_version: str = "1.0"
