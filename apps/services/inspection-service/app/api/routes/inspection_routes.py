from fastapi import APIRouter, Depends, HTTPException

from app.application.services.inspection_service import InspectionApplicationService
from app.infrastructure.repositories.inspection_repository import InspectionRepository

router = APIRouter(prefix="/inspections", tags=["inspections"])


def get_inspection_service() -> InspectionApplicationService:
    return InspectionApplicationService(InspectionRepository())


@router.post("")
async def create_inspection(
    payload: dict,
    service: InspectionApplicationService = Depends(get_inspection_service),
):
    try:
        inspection = service.create_inspection(
            inspection_id=payload["inspection_id"],
            asset_id=payload["asset_id"],
            tenant_id=payload["tenant_id"],
        )
        return {
            "inspection_id": inspection.inspection_id,
            "asset_id": inspection.asset_id,
            "tenant_id": inspection.tenant_id,
            "findings": [finding.__dict__ for finding in inspection.findings],
            "inspected_at": inspection.inspected_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{inspection_id}/findings")
async def add_finding(
    inspection_id: str,
    payload: dict,
    service: InspectionApplicationService = Depends(get_inspection_service),
):
    try:
        inspection = service.add_finding(
            inspection_id,
            finding_id=payload["finding_id"],
            finding_type=payload["finding_type"],
            description=payload["description"],
            severity=payload.get("severity", "unknown"),
        )
        return {
            "inspection_id": inspection.inspection_id,
            "findings": [finding.__dict__ for finding in inspection.findings],
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("")
async def list_inspections(
    tenant_id: str,
    asset_id: str | None = None,
    service: InspectionApplicationService = Depends(get_inspection_service),
):
    inspections = service.list_inspections(tenant_id, asset_id)
    return [
        {
            "inspection_id": item.inspection_id,
            "asset_id": item.asset_id,
            "tenant_id": item.tenant_id,
            "findings": [finding.__dict__ for finding in item.findings],
            "inspected_at": item.inspected_at.isoformat(),
        }
        for item in inspections
    ]
