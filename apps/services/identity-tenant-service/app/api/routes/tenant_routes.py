from fastapi import APIRouter, Depends, HTTPException

from app.application.services.tenant_service import TenantApplicationService
from app.infrastructure.repositories.tenant_repository import TenantRepository

router = APIRouter(prefix="/tenants", tags=["tenants"])


def get_tenant_service() -> TenantApplicationService:
    return TenantApplicationService(TenantRepository())


@router.post("")
async def create_tenant(
    payload: dict,
    service: TenantApplicationService = Depends(get_tenant_service),
):
    try:
        tenant = service.create_tenant(
            tenant_id=payload["tenant_id"],
            name=payload["name"],
        )
        return {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "status": tenant.status,
            "roles": tenant.roles,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    service: TenantApplicationService = Depends(get_tenant_service),
):
    try:
        tenant = service.get_tenant(tenant_id)
        return {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "status": tenant.status,
            "roles": tenant.roles,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
