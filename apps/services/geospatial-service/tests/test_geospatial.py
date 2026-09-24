from fastapi.testclient import TestClient

from app.api import repository
from app.main import app


client = TestClient(app)
POLYGON = {
    "type": "Polygon",
    "coordinates": [[[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]]],
}


def setup_function():
    repository.layers.clear()
    repository.locations.clear()
    repository.exposures.clear()
    repository.vegetation.clear()
    repository.vegetation_exposures.clear()


def layer():
    response = client.post("/api/v1/hazard-layers", json={
        "tenant_id": "tenant-a", "hazard_type": "flood", "source": "feed",
        "source_uri": "https://example.test/flood", "source_observed_at": "2026-01-01T00:00:00Z",
        "geometry": POLYGON, "properties": {"severity": "high"},
    })
    assert response.status_code == 201
    return response.json()


def test_ingestion_is_append_only_and_geojson_is_tenant_scoped():
    first = layer()
    second = layer()
    assert first["layer_snapshot_id"] != second["layer_snapshot_id"]
    response = client.get("/api/v1/hazard-layers", params={"tenant_id": "tenant-a"})
    assert response.status_code == 200
    assert len(response.json()["features"]) == 2
    assert response.json()["features"][0]["properties"]["severity"] == "high"


def test_location_and_point_in_polygon_exposure():
    snapshot = layer()
    location = client.post("/api/v1/asset-locations", json={
        "asset_id": "asset-1", "tenant_id": "tenant-a", "longitude": 0,
        "latitude": 0, "source": "asset-registry", "observed_at": "2026-01-01T00:00:00Z",
    }).json()
    response = client.post("/api/v1/exposures/evaluate", json={
        "asset_id": "asset-1", "tenant_id": "tenant-a",
        "layer_snapshot_id": snapshot["layer_snapshot_id"],
        "location_id": location["location_id"],
    })
    assert response.status_code == 200
    assert response.json()["intersection_type"] == "inside"
    assert response.json()["exposure_score"] == 1


def test_point_outside_polygon_has_no_exposure():
    snapshot = layer()
    response = client.post("/api/v1/exposures/evaluate", json={
        "asset_id": "asset-2", "tenant_id": "tenant-a",
        "layer_snapshot_id": snapshot["layer_snapshot_id"],
        "longitude": 5, "latitude": 5,
    })
    assert response.status_code == 200
    assert response.json()["intersection_type"] == "none"
    assert response.json()["exposure_score"] == 0


def test_vegetation_exposure_is_versioned_and_asset_scoped():
    response = client.post("/api/v1/vegetation", json={
        "tenant_id": "tenant-a",
        "source": "vegetation-feed",
        "source_observed_at": "2026-01-01T00:00:00Z",
        "geometry": POLYGON,
        "vegetation_type": "dead_tree",
        "strike_potential": 85,
        "asset_ids": ["asset-1", "asset-2"],
    })
    assert response.status_code == 201
    snapshot = response.json()
    exposure = client.post("/api/v1/vegetation/exposures/evaluate", json={
        "tenant_id": "tenant-a",
        "asset_id": "asset-1",
        "vegetation_snapshot_id": snapshot["vegetation_snapshot_id"],
        "longitude": 0,
        "latitude": 0,
    })
    assert exposure.status_code == 200
    assert exposure.json()["exposure_score"] == 85
    assert exposure.json()["intersection_type"] == "inside"
