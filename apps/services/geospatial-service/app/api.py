from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from libs.common.geospatial_domain import (
    AssetHazardExposure,
    AssetLocationSnapshot,
    GeoPoint,
    HazardLayerSnapshot,
)
from app.domain.geometry import point_in_geometry
from app.infrastructure.repository import GeospatialRepository
from app.infrastructure.repository import VegetationExposure, VegetationSnapshot
from app.schemas import (
    ExposureIn,
    ExposureOut,
    HazardLayerIn,
    LocationIn,
    VegetationExposureIn,
    VegetationExposureOut,
    VegetationGeometryIn,
)

router = APIRouter(prefix="/api/v1", tags=["geospatial"])
repository = GeospatialRepository()


def get_repository() -> GeospatialRepository:
    return repository


@router.post("/hazard-layers", status_code=201)
def ingest_hazard_layer(payload: HazardLayerIn, repo: GeospatialRepository = Depends(get_repository)):
    if payload.geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise HTTPException(status_code=422, detail="geometry must be a Polygon or MultiPolygon")
    layer = HazardLayerSnapshot(
        layer_snapshot_id=str(uuid4()), tenant_id=payload.tenant_id,
        hazard_type=payload.hazard_type, source=payload.source, source_uri=payload.source_uri,
        source_observed_at=payload.source_observed_at, ingested_at=datetime.now(timezone.utc),
        valid_from=payload.valid_from, valid_to=payload.valid_to, geometry=payload.geometry,
        properties=payload.properties,
        source_event_id=payload.source_event_id or str(uuid4()),
    )
    return asdict(repo.add_layer(layer))


@router.post("/asset-locations", status_code=201)
def record_location(payload: LocationIn, repo: GeospatialRepository = Depends(get_repository)):
    location = AssetLocationSnapshot(
        location_id=str(uuid4()), asset_id=payload.asset_id, tenant_id=payload.tenant_id,
        point=GeoPoint(latitude=payload.latitude, longitude=payload.longitude),
        source=payload.source, observed_at=payload.observed_at,
    )
    result = asdict(repo.add_location(location))
    result["point"] = asdict(location.point)
    return result


@router.get("/hazard-layers", response_model=dict[str, Any])
def get_hazard_layers(tenant_id: str = Query(...), repo: GeospatialRepository = Depends(get_repository)):
    return repo.layer_geojson(tenant_id)


@router.get("/hazard-layers/{tenant_id}", response_model=dict[str, Any], include_in_schema=False)
def get_hazard_layers_by_tenant(tenant_id: str, repo: GeospatialRepository = Depends(get_repository)):
    return repo.layer_geojson(tenant_id)


@router.post("/exposures/evaluate", response_model=ExposureOut)
def evaluate_exposure(payload: ExposureIn, repo: GeospatialRepository = Depends(get_repository)):
    layer = next((item for item in repo.layers
                  if item.layer_snapshot_id == payload.layer_snapshot_id
                  and item.tenant_id == payload.tenant_id), None)
    if layer is None:
        raise HTTPException(status_code=404, detail="Hazard layer snapshot not found")
    location = None
    if payload.location_id:
        location = next((item for item in repo.locations
                         if item.location_id == payload.location_id
                         and item.tenant_id == payload.tenant_id
                         and item.asset_id == payload.asset_id), None)
        if location is None:
            raise HTTPException(status_code=404, detail="Asset location snapshot not found")
    elif payload.longitude is None or payload.latitude is None:
        raise HTTPException(status_code=422, detail="location_id or longitude and latitude are required")
    longitude = location.point.longitude if location else payload.longitude
    latitude = location.point.latitude if location else payload.latitude
    inside = point_in_geometry((longitude, latitude), layer.geometry)
    exposure = AssetHazardExposure(
        exposure_id=str(uuid4()), asset_id=payload.asset_id, tenant_id=payload.tenant_id,
        layer_snapshot_id=layer.layer_snapshot_id, hazard_type=layer.hazard_type,
        exposure_score=1.0 if inside else 0.0,
        intersection_type="inside" if inside else "none",
        evidence={"longitude": longitude, "latitude": latitude},
    )
    return repo.add_exposure(exposure)


@router.post("/vegetation", status_code=201)
def ingest_vegetation(
    payload: VegetationGeometryIn,
    repo: GeospatialRepository = Depends(get_repository),
) -> dict[str, Any]:
    if payload.geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise HTTPException(
            status_code=422,
            detail="geometry must be a Polygon or MultiPolygon",
        )
    snapshot = VegetationSnapshot(
        vegetation_snapshot_id=str(uuid4()),
        tenant_id=payload.tenant_id,
        source=payload.source,
        source_observed_at=payload.source_observed_at,
        geometry=payload.geometry,
        vegetation_type=payload.vegetation_type,
        clearance_distance_ft=payload.clearance_distance_ft,
        strike_potential=payload.strike_potential,
        growth_rate=payload.growth_rate,
        asset_ids=list(payload.asset_ids),
        ingested_at=datetime.now(timezone.utc),
    )
    return asdict(repo.add_vegetation(snapshot))


@router.post(
    "/vegetation/exposures/evaluate",
    response_model=VegetationExposureOut,
)
def evaluate_vegetation_exposure(
    payload: VegetationExposureIn,
    repo: GeospatialRepository = Depends(get_repository),
) -> VegetationExposure:
    snapshot = next(
        (
            item
            for item in repo.vegetation
            if item.vegetation_snapshot_id == payload.vegetation_snapshot_id
            and item.tenant_id == payload.tenant_id
        ),
        None,
    )
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Vegetation snapshot not found")
    location = None
    if payload.location_id:
        location = next(
            (
                item
                for item in repo.locations
                if item.location_id == payload.location_id
                and item.tenant_id == payload.tenant_id
                and item.asset_id == payload.asset_id
            ),
            None,
        )
        if location is None:
            raise HTTPException(status_code=404, detail="Asset location snapshot not found")
    elif payload.longitude is None or payload.latitude is None:
        raise HTTPException(
            status_code=422,
            detail="location_id or longitude and latitude are required",
        )
    longitude = location.point.longitude if location else payload.longitude
    latitude = location.point.latitude if location else payload.latitude
    inside = point_in_geometry((longitude, latitude), snapshot.geometry)
    score = snapshot.strike_potential if inside and snapshot.strike_potential is not None else (
        1.0 if inside else 0.0
    )
    exposure = VegetationExposure(
        exposure_id=str(uuid4()),
        tenant_id=payload.tenant_id,
        asset_id=payload.asset_id,
        vegetation_snapshot_id=snapshot.vegetation_snapshot_id,
        exposure_score=score,
        intersection_type="inside" if inside else "none",
        evaluated_at=datetime.now(timezone.utc),
        evidence={
            "longitude": longitude,
            "latitude": latitude,
            "source_observed_at": snapshot.source_observed_at.isoformat(),
        },
    )
    return repo.add_vegetation_exposure(exposure)
