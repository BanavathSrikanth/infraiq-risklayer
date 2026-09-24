from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    wind_speed_mph: float = Field(default=0.0, ge=0)
    temperature_f: float = Field(default=70.0)
    relative_humidity_pct: float = Field(default=50.0, ge=0, le=100)
    precipitation_in: float = Field(default=0.0, ge=0)
    fire_weather_index: Optional[float] = Field(default=None, ge=0, le=100)

    observed_at: Optional[datetime] = None
    source: Optional[str] = None


class AhsInput(BaseModel):
    age_years: float = Field(ge=0)
    material: str
    remaining_fiber_pct: float = Field(ge=0, le=100)
    defect_severity: str
    lean_deg: float = Field(default=0.0, ge=0)
    attachment_count: int = Field(default=0, ge=0)
    asset_class: str
    reinforced_within_10_years: bool = False


class CesInput(BaseModel):
    hftd_tier: Literal["none", "tier_1", "tier_2", "tier_3"]
    fhsz_level: Literal["none", "moderate", "high", "very_high"]
    landfire_ros_class: int = Field(ge=1, le=5)
    slope_deg: float = Field(ge=0)
    p95_historical_gust_mps: float = Field(ge=0)
    soil_decay_zone_exposure: float | None = Field(default=None, ge=0, le=1)
    floodplain_exposure: float | None = Field(default=None, ge=0, le=1)


class CqsInput(BaseModel):
    population_density_1km: float = Field(ge=0)
    critical_facilities_2km: int = Field(ge=0)
    customers_on_circuit_segment: int = Field(ge=0)
    road_density: float = Field(ge=0)


class VesInput(BaseModel):
    proximity_factor: float = Field(ge=0, le=1)
    density_factor: float = Field(ge=0, le=1)
    clearance_factor: float = Field(ge=0, le=1)
    overlap_factor: float = Field(ge=0, le=1)
    encroach_factor: float = Field(ge=0, le=1)


class HazardExposureInput(BaseModel):
    hazard_type: str = Field(min_length=1)
    exposure_score: float = Field(ge=0, le=100)
    layer_snapshot_id: str = Field(min_length=1)
    source_observed_at: datetime
    source: str = Field(min_length=1)


class RiskInput(BaseModel):
    asset_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)

    calculated_at: Optional[datetime] = None

    ahs: AhsInput
    ces: CesInput
    cqs: CqsInput

    weather: WeatherInput = Field(
        default_factory=WeatherInput
    )

    time_sensitivity: float = Field(
        default=0,
        ge=0,
        le=100,
    )
    days_overdue: float = Field(default=0, ge=0)
    work_already_scheduled: bool = False
    stale_feeds: list[str] = Field(default_factory=list)
    imputed_feeds: list[str] = Field(default_factory=list)
    missing_feeds: list[str] = Field(default_factory=list)
    critical_missing_feeds: list[str] = Field(default_factory=list)

    ves: VesInput

    hazard_exposures: list[HazardExposureInput] = Field(default_factory=list)


class RiskBlobIngestionRequest(BaseModel):
    blob_name: str = Field(min_length=1)
    tenant_id: Optional[str] = Field(default=None, min_length=1)