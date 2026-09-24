from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HazardLayerIn(BaseModel):
    tenant_id: str
    hazard_type: str
    source: str
    source_uri: str
    source_observed_at: datetime
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    geometry: dict[str, Any]
    properties: dict[str, Any] = Field(default_factory=dict)
    source_event_id: str | None = None


class LocationIn(BaseModel):
    asset_id: str
    tenant_id: str
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)
    source: str
    observed_at: datetime


class ExposureIn(BaseModel):
    asset_id: str
    tenant_id: str
    layer_snapshot_id: str
    location_id: str | None = None
    longitude: float | None = Field(default=None, ge=-180, le=180)
    latitude: float | None = Field(default=None, ge=-90, le=90)


class ExposureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exposure_id: str
    asset_id: str
    tenant_id: str
    layer_snapshot_id: str
    hazard_type: str
    exposure_score: float
    intersection_type: str
    evaluated_at: datetime
    evidence: dict[str, Any]


class VegetationGeometryIn(BaseModel):
    tenant_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_observed_at: datetime
    geometry: dict[str, Any]
    vegetation_type: str | None = None
    clearance_distance_ft: float | None = Field(default=None, ge=0)
    strike_potential: float | None = Field(default=None, ge=0, le=100)
    growth_rate: float | None = Field(default=None, ge=0)
    asset_ids: list[str] = Field(default_factory=list)


class VegetationExposureIn(BaseModel):
    tenant_id: str = Field(min_length=1)
    asset_id: str = Field(min_length=1)
    vegetation_snapshot_id: str = Field(min_length=1)
    location_id: str | None = None
    longitude: float | None = Field(default=None, ge=-180, le=180)
    latitude: float | None = Field(default=None, ge=-90, le=90)


class VegetationExposureOut(BaseModel):
    exposure_id: str
    tenant_id: str
    asset_id: str
    vegetation_snapshot_id: str
    exposure_score: float
    intersection_type: str
    evaluated_at: datetime
    evidence: dict[str, Any]
