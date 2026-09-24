from datetime import datetime, timezone

from app.domain.entities.report import Report
from app.infrastructure.repositories.report_repository import ReportRepository


class ReportApplicationService:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    def create_report(self, report_id: str, asset_id: str, tenant_id: str, report_type: str) -> Report:
        report = Report(
            report_id=report_id,
            asset_id=asset_id,
            tenant_id=tenant_id,
            report_type=report_type,
            status="generated",
            generated_at=datetime.now(timezone.utc),
        )
        return self.repository.save(report)

    def list_reports(self, tenant_id: str) -> list[Report]:
        return self.repository.list_by_tenant(tenant_id)
