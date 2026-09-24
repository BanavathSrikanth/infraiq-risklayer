from app.domain.entities.inspection import Inspection
from app.infrastructure.repositories.inspection_repository import InspectionRepository


class InspectionApplicationService:
    def __init__(self, repository: InspectionRepository):
        self.repository = repository

    def create_inspection(self, inspection_id: str, asset_id: str, tenant_id: str) -> Inspection:
        inspection = Inspection(
            inspection_id=inspection_id,
            asset_id=asset_id,
            tenant_id=tenant_id,
            findings=[],
        )
        return self.repository.save(inspection)

    def add_finding(
        self,
        inspection_id: str,
        finding_id: str,
        finding_type: str,
        description: str,
        severity: str = "unknown",
    ) -> Inspection:
        inspection = self.repository.get_by_id(inspection_id)
        if inspection is None:
            raise ValueError(f"Inspection {inspection_id} not found")

        inspection.add_finding(
            finding_id=finding_id,
            finding_type=finding_type,
            description=description,
            severity=severity,
        )
        return self.repository.update(inspection)

    def list_inspections(self, tenant_id: str, asset_id: str | None = None) -> list[Inspection]:
        return self.repository.list_by_tenant(tenant_id, asset_id)
