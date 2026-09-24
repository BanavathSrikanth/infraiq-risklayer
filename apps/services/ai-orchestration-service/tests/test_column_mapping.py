from pathlib import Path

from app.application.column_mapping.profiler import profile_file
from app.application.column_mapping.service import ColumnMappingService
from app.config import Settings
from app.domain.schemas.column_mapping import ReviewMappingRequest


def test_profiler_infers_csv_columns():
    profiles = profile_file(
        "claims.csv",
        b"policy_no,loss_dt,amount\nP-001,2026-01-02,12.5\n",
    )

    assert [profile.name for profile in profiles] == ["policy_no", "loss_dt", "amount"]
    assert profiles[1].inferred_type == "date"
    assert profiles[2].inferred_type == "number"


def test_mapping_can_be_reviewed_and_persisted(tmp_path: Path):
    source = tmp_path / "claims.csv"
    source.write_text("policy_no,loss_dt\nP-001,2026-01-02\n", encoding="utf-8")
    settings = Settings(mapping_store_path=str(tmp_path / "mappings.json"))
    service = ColumnMappingService(settings)

    record = service.propose(
        tenant_id="tenant-1",
        schema_name="claim",
        source_uri=f"file://{source}",
        target_fields=["policy_no", "loss_dt"],
    )
    reviewed = service.review(
        record.mapping_id,
        ReviewMappingRequest(reviewer="analyst-1", decision="approved"),
    )

    assert reviewed.status == "approved"
    assert reviewed.reviewed_by == "analyst-1"
    assert service.store.get(record.mapping_id).status == "approved"