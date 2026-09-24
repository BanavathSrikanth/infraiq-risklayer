from app.domain.models import MappingSpec, Source, SourceType
from app.domain.pipeline import IntegrationPipeline
from app.infrastructure.blob import InMemoryBlobLandingAdapter
from app.infrastructure.repository import InMemoryIntegrationRepository


def test_csv_is_profiled_validated_and_normalized_without_raw_scoring_input():
    repo = InMemoryIntegrationRepository()
    source = repo.save(Source(tenant_id="t1", source_key="assets", name="Assets", source_type=SourceType.csv))
    pipeline = IntegrationPipeline(repo, InMemoryBlobLandingAdapter())
    result = pipeline.ingest(
        source,
        b"asset,when,value\nA-1,2026-01-01T00:00:00Z,12\n,2026-01-01T00:00:00Z,4\n",
        "text/csv",
        MappingSpec(source_id=source.id, canonical_fields={"asset_id": "asset", "observed_at": "when", "value": "value"}),
    )
    assert result.profile.row_count == 2
    assert result.classification.schema_family == "generic"
    assert result.status == "quarantined"
    assert len(result.canonical_records) == 1
    assert len(result.quarantine) == 1
    assert result.canonical_records[0].asset_id == "A-1"
    assert not hasattr(result.canonical_records[0], "value")
    assert result.provenance[0].source_values["value"] == "12"


def test_json_object_is_supported():
    repo = InMemoryIntegrationRepository()
    source = repo.save(Source(tenant_id="t1", source_key="api", name="API", source_type=SourceType.api))
    result = IntegrationPipeline(repo, InMemoryBlobLandingAdapter()).ingest(
        source,
        b'{"id":"A-2","time":"2026-01-01T00:00:00Z"}',
        "application/json",
        MappingSpec(source_id=source.id, canonical_fields={"asset_id": "id", "observed_at": "time"}),
    )
    assert len(result.canonical_records) == 1
