from typing import Dict, List

from app.domain.entities.report import Report


class ReportRepository:
    def __init__(self):
        self._store: Dict[str, Report] = {}

    def save(self, report: Report) -> Report:
        self._store[report.report_id] = report
        return report

    def list_by_tenant(self, tenant_id: str) -> List[Report]:
        return [item for item in self._store.values() if item.tenant_id == tenant_id]
