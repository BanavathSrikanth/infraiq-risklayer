from typing import Any
from dataclasses import dataclass
from datetime import datetime

from libs.common.geospatial_domain import (
    AssetHazardExposure,
    AssetLocationSnapshot,
    HazardLayerSnapshot,
)

@dataclass(frozen=True)
class VegetationSnapshot:
    vegetation_snapshot_id: str
    tenant_id: str
    source: str
    source_observed_at: datetime
    geometry: dict[str, Any]
    vegetation_type: str | None
    clearance_distance_ft: float | None
    strike_potential: float | None
    growth_rate: float | None
    asset_ids: list[str]
    ingested_at: datetime


@dataclass(frozen=True)
class VegetationExposure:
    exposure_id: str
    tenant_id: str
    asset_id: str
    vegetation_snapshot_id: str
    exposure_score: float
    intersection_type: str
    evaluated_at: datetime
    evidence: dict[str, Any]


class GeospatialRepository:
    """In-memory append-only store used by the minimal service."""

    def __init__(self) -> None:
        self.layers: list[HazardLayerSnapshot] = []
        self.locations: list[AssetLocationSnapshot] = []
        self.exposures: list[AssetHazardExposure] = []
        self.vegetation: list[VegetationSnapshot] = []
        self.vegetation_exposures: list[VegetationExposure] = []

    def add_layer(self, layer: HazardLayerSnapshot) -> HazardLayerSnapshot:
        self.layers.append(layer)
        return layer

    def add_location(self, location: AssetLocationSnapshot) -> AssetLocationSnapshot:
        self.locations.append(location)
        return location

    def add_exposure(self, exposure: AssetHazardExposure) -> AssetHazardExposure:
        self.exposures.append(exposure)
        return exposure

    def add_vegetation(self, snapshot: VegetationSnapshot) -> VegetationSnapshot:
        self.vegetation.append(snapshot)
        return snapshot

    def add_vegetation_exposure(
        self, exposure: VegetationExposure
    ) -> VegetationExposure:
        self.vegetation_exposures.append(exposure)
        return exposure

    def layer_geojson(self, tenant_id: str) -> dict[str, Any]:
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": layer.layer_snapshot_id,
                    "geometry": layer.geometry,
                    "properties": {
                        **layer.properties,
                        "layer_snapshot_id": layer.layer_snapshot_id,
                        "tenant_id": layer.tenant_id,
                        "hazard_type": layer.hazard_type,
                        "source": layer.source,
                        "source_uri": layer.source_uri,
                        "source_observed_at": layer.source_observed_at.isoformat(),
                        "ingested_at": layer.ingested_at.isoformat(),
                    },
                }
                for layer in self.layers
                if layer.tenant_id == tenant_id
            ],
        }
