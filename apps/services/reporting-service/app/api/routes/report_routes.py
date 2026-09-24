from fastapi import APIRouter, Depends, HTTPException

from app.application.services.report_service import ReportApplicationService
from app.infrastructure.repositories.report_repository import ReportRepository

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service() -> ReportApplicationService:
    return ReportApplicationService(ReportRepository())


@router.post("")
async def create_report(
    payload: dict,
    service: ReportApplicationService = Depends(get_report_service),
):
    try:
        report = service.create_report(
            report_id=payload["report_id"],
            asset_id=payload["asset_id"],
            tenant_id=payload["tenant_id"],
            report_type=payload["report_type"],
        )
        return {
            "report_id": report.report_id,
            "asset_id": report.asset_id,
            "tenant_id": report.tenant_id,
            "report_type": report.report_type,
            "status": report.status,
            "generated_at": report.generated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
