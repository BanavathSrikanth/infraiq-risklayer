# Geospatial Service

The geospatial service owns spatial projections and immutable hazard-layer
snapshots. It does not become a second asset registry and it does not own the
authoritative risk score.

## Data flow

1. Asset service publishes or exposes the authoritative asset identity and
   current location.
2. Hazard adapters ingest live heat, flood, wind, fire, vegetation, or other
   feeds into immutable `HazardLayerSnapshot` records.
3. The service normalizes source geometries to GeoJSON using WGS84
   (`EPSG:4326`) for MapLibre and stores source timestamps and provenance.
4. A spatial join evaluates each asset point against the relevant polygon or
   raster-derived geometry and creates an immutable `AssetHazardExposure`.
5. Risk service consumes the exposure snapshot as input to a new risk
   evaluation. It never changes an earlier evaluation.
6. A separate prioritization calculation creates a
   `PolePriorityEvaluation`; priority is not the same thing as risk.

## MapLibre contract

MapLibre should consume:

- a stable style document
- base-map tiles
- a tenant-scoped hazard `FeatureCollection` or vector-tile source
- asset points from an asset projection
- risk/priority properties as display attributes

The map is a read projection. Editing a marker or polygon must call the owning
service and create a new versioned record; the map must not directly mutate
history.

## Live data rules

Every feed observation stores its provider, source URI, observation time,
ingestion time, validity interval, raw/source reference, normalized geometry,
and source event identifier. A newer feed observation creates a new snapshot.
It does not overwrite the earlier weather or hazard snapshot.

## Minimal HTTP API

Run locally from this directory with `uvicorn app.main:app --reload`.
The service uses an append-only in-memory repository by default; the repository
is an explicit boundary for replacing it with durable storage or a spatial
index.

- `POST /api/v1/hazard-layers` ingests a Polygon or MultiPolygon snapshot.
- `POST /api/v1/asset-locations` records an immutable WGS84 location snapshot.
- `GET /api/v1/hazard-layers?tenant_id=...` returns a tenant-scoped GeoJSON
  `FeatureCollection`.
- `POST /api/v1/exposures/evaluate` evaluates a location snapshot (or supplied
  point) against a hazard snapshot and records an immutable exposure.

No spatial package is required. The included implementation supports GeoJSON
Polygon and MultiPolygon rings, including polygon holes. A database-backed
spatial implementation can replace `app.domain.geometry` without changing
these contracts.
