# InfraIQ Asset Intelligence API

FastAPI service for assets, inspections, GIS, and risk calculation. The HTTP contract is OpenAPI at `/docs` and `/openapi.json`, so React, .NET, and other clients can generate typed clients without importing Python code.

## Run locally

```powershell
cd infraiq-risklayer/apps/services/risk-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "$(Get-Location).Path;$(Resolve-Path ..\..\..)"
uvicorn app.api.main:app --reload
```

Open `http://localhost:8000/docs`.

## Run with Docker

```powershell
copy .env.example .env
docker compose up --build
```

Azure Blob Storage is enabled when `BLOB_CONNECTION_STRING` is set. Redis is enabled through `REDIS_URL`. Azure AI Foundry settings are reserved in `FOUNDRY_ENDPOINT` and `FOUNDRY_API_KEY`; no credential is committed to the repository.

## API resources

- `POST/GET /api/v1/assets`: asset master data and lifecycle state.
- `POST/GET /api/v1/inspections`: inspection observations and evidence metadata.
- `PUT/GET /api/v1/gis/assets/{asset_id}`: asset coordinates.
- `GET /api/v1/gis/map-config`: MapLibre style and OSM tile configuration.
- `GET /api/v1/gis/geocode?query=...`: OSM Nominatim geocoding.
- `POST /api/v1/inspections/{inspection_id}/evidence`: upload raw inspection evidence to Blob Storage; send the filename in `X-File-Name` and the MIME type in `Content-Type`.
- `POST /api/v1/risks/calculate`: calculate a versioned risk result.
- `POST /api/v1/risks/ingest/blob`: download a UTF-8 CSV from Blob Storage,
  calculate and persist valid rows, and return row-level errors for invalid
  rows. The JSON body is `{"blob_name": "...", "tenant_id": "..."}`; the
  tenant is optional, but when supplied it rejects rows for other tenants.
  CSV headers use dotted `RiskInput` paths (for example
  `ahs.age_years`, `ces.hftd_tier`, `cqs.road_density`,
  `weather.wind_speed_mph`, `days_overdue`, and
  `ves.proximity_factor`). `stale_feeds`, `imputed_feeds`, and hazard
  exposures can be JSON arrays.
- `GET /api/v1/risks/latest/{asset_id}`: read the cached result when Redis is configured.
- `GET /api/v1/risks/history/{asset_id}`: read append-only risk evaluations.
- `POST /api/v1/risks/pole-priority`: calculate a versioned pole work-priority score; this does not authorize replacement or assign work.

Every resource carries `tenant_id`; production authentication should derive that value from a validated token rather than trusting arbitrary client input.

## Formula governance

The v1.1 composite risk score uses the Asset Health Score (AHS), Chronic
Exposure Score (CES), Consequence Score (CQS), and Vegetation Exposure Score
(VES):

`risk_score = 0.35 * AHS + 0.20 * CES + 0.25 * CQS + 0.20 * VES`

The weights and thresholds are versioned in `app/domain/rules/v1/*.yaml`.
The composite weights sum to `1.0`; DHM and OPS remain calculated outputs but
are not included in the composite risk score.

VES v2.0 is calculated from normalized vegetation factors:

`VES = 100 * clamp(0.25 * proximity + 0.20 * density + 0.30 * clearance + 0.15 * overlap + 0.10 * encroach, 0, 1)`

The five VES inputs must each be normalized to `0-1` before calculation.
Inspection evidence and source lineage remain separate metadata and do not
change the VES score.

CES v2.0 is the Chronic Exposure Score:

`CES = 100 * clamp(0.35 * HFTD + 0.20 * FHSZ + 0.20 * fuel + 0.15 * slope + 0.10 * historical_wind, 0, 1)`

HFTD and FHSZ use the configured categorical factors. Fuel is the LANDFIRE
rate-of-spread class divided by 5, slope is `min(1, slope_deg / 45)`, and
historical wind is `min(1, p95_historical_gust_mps / 30)`. Soil/decay-zone
and floodplain exposure remain optional chronic factors and are not part of
the v2.0 weighted score until approved weights are defined. Real-time weather
continues to be calculated separately by the Dynamic Hazard Monitor (DHM).

OPS uses the v1.1 Operational Priority Score formula:

`base = 0.40 * AHS + 0.25 * CES + 0.35 * CQS`

`DHM_multiplier = clamp(base, 1.0, 2.5)`

`OPS = clamp(base * DHM_multiplier + min(15, (days_overdue / 30) * 5) - (10 if work_already_scheduled else 0), 0, 100)`

When a contributing feed is stale, its request value must be the last known
value and the result is marked `stale=true`; stale values are never replaced
with a default score.

Confidence is calculated independently from the score as the product across
the required AHS, CES, CQS, DHM, and VES feeds: `1.0` for present and fresh,
`0.8` for present but beyond SLA, `0.5` for distribution-imputed, and `0.3`
for missing. A missing critical input caps confidence at `0.5` and adds a
visible warning. Confidence never reduces the calculated risk score.
When dataset columns are omitted, the result also identifies the exact
nested columns, such as `weather.wind_speed_mph` or
`cqs.population_density_1km`.

Do not put formula constants in routes or frontend code. A rule change creates a new rule version and should receive new regression tests.

## Spatial hazard and pole priority

The geospatial service provides timestamped hazard exposures from live heat,
flood, wind, fire, and related polygon layers. The risk API consumes those
exposures as immutable inputs. Pole prioritization is a separate, versioned
queue calculation combining risk, hazard exposure, consequence, urgency, and
inspection confidence. Its result is advisory for routing and planning; an
authorized decision is still required for consequential work such as pole
replacement.

## Column mapping

| Source column | API field | Domain meaning | Unit / constraints |
|---|---|---|---|
| `asset_id` | `AssetCreate.asset_id` | Stable asset identifier | Non-empty string |
| `tenant_id` | `*.tenant_id` | Customer or organizational boundary | Non-empty string |
| `asset_class` | `AssetCreate.asset_class` / `RiskInput.ahs.asset_class` | Distribution or transmission class | String matching configured rules |
| `material` | `AssetCreate.material` / `RiskInput.ahs.material` | Physical material | Rule key such as `wood`, `steel`, `concrete` |
| `inspection_date` | `InspectionCreate.inspected_at` | Observation time | ISO-8601 UTC datetime |
| `defect_severity` | `InspectionCreate.defect_severity` / `RiskInput.ahs.defect_severity` | Defect severity category | `none`, `minor`, `moderate`, `major`, `critical` |
| `condition_score` | `InspectionCreate.condition_score` | Normalized inspection condition | 0-100 |
| `hftd_tier` | `RiskInput.ces.hftd_tier` | Chronic high-fire-threat district tier | `none`, `tier_1`, `tier_2`, `tier_3` |
| `fhsz_level` | `RiskInput.ces.fhsz_level` | Chronic fire-hazard severity zone | `none`, `moderate`, `high`, `very_high` |
| `landfire_ros_class` | `RiskInput.ces.landfire_ros_class` | LANDFIRE rate-of-spread class | Integer 1-5 |
| `slope_deg` | `RiskInput.ces.slope_deg` | Chronic terrain slope | Non-negative degrees |
| `p95_historical_gust_mps` | `RiskInput.ces.p95_historical_gust_mps` | Historical 95th-percentile gust | Non-negative m/s |
| `population_density_1km` | `RiskInput.cqs.population_density_1km` | Population density within 1 km | Non-negative people/km² |
| `critical_facilities_2km` | `RiskInput.cqs.critical_facilities_2km` | Schools, hospitals, and fire stations within 2 km | Non-negative integer |
| `customers_on_circuit_segment` | `RiskInput.cqs.customers_on_circuit_segment` | Customers served by the circuit segment | Non-negative integer |
| `road_density` | `RiskInput.cqs.road_density` | Road density used for egress constraint | Non-negative, normalized against configured maximum |
| `latitude` / `longitude` | `AssetCreate.latitude` / `AssetCreate.longitude` | Asset location | WGS84 degrees |
| `evidence_blob_name` | `InspectionCreate.evidence_blob_name` | Blob reference | Blob name, never raw secret |

For .NET, generate a client from `/openapi.json` with NSwag or Kiota. For React, generate TypeScript types or use the same OpenAPI document with Orval; send ISO-8601 dates and preserve numeric fields as numbers.
