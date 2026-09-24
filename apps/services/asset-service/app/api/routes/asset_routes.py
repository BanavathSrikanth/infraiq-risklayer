from fastapi import APIRouter, Depends, HTTPException

from app.application.services.asset_service import AssetApplicationService
from app.infrastructure.repositories.asset_repository import AssetRepository

router = APIRouter(prefix="/assets", tags=["assets"])


def get_asset_service() -> AssetApplicationService:
    return AssetApplicationService(AssetRepository())


@router.post("")
async def create_asset(
    payload: dict,
    service: AssetApplicationService = Depends(get_asset_service),
):
    try:
        asset = service.register_asset(
            asset_id=payload["asset_id"],
            tenant_id=payload["tenant_id"],
            name=payload["name"],
            asset_type=payload["asset_type"],
            location=payload["location"],
        )
        return {
            "asset_id": asset.asset_id,
            "tenant_id": asset.tenant_id,
            "name": asset.name,
            "status": asset.status,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{asset_id}")
async def get_asset(
    asset_id: str,
    service: AssetApplicationService = Depends(get_asset_service),
):
    try:
        asset = service.get_asset(asset_id)
        return {
            "asset_id": asset.asset_id,
            "tenant_id": asset.tenant_id,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "location": asset.location,
            "status": asset.status,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{asset_id}/status")
async def update_asset_status(
    asset_id: str,
    payload: dict,
    service: AssetApplicationService = Depends(get_asset_service),
):
    try:
        asset = service.update_status(asset_id, payload["status"])
        return {
            "asset_id": asset.asset_id,
            "status": asset.status,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
