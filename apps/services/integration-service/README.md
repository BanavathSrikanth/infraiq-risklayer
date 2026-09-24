# Integration / Source Data Service

This service enforces the source-data boundary:
**Source Registry → Classification → Raw Landing → Profiling → Mapping → Validation →
Quarantine → Normalization → Canonical model → Provenance**.

Raw files are landed through `BlobLandingAdapter` and are never sent to scoring.
Only validated `CanonicalRecord` instances are persisted/emitted downstream; invalid
rows remain in the quarantine result with actionable validation issues.

For production Blob Storage landing, set `BLOB_CONNECTION_STRING` and optionally
`BLOB_CONTAINER` (default: `infraiq`). The adapter writes content-addressed,
immutable objects below `raw/{source_id}/{sha256}` and refuses reads from another
container. Use managed identity in Azure deployments by replacing the connection
string adapter with the repository's `BlobLandingAdapter` implementation.

The in-memory adapters remain available only for tests and local development.

Run locally from the repository root:

```powershell
uvicorn --app-dir apps/services/integration-service app.main:app --reload
```
