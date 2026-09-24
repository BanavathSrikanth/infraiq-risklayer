from app.domain.entities.asset import Asset
from app.infrastructure.repositories.asset_repository import AssetRepository


class AssetApplicationService:
    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def register_asset(
        self,
        asset_id: str,
        tenant_id: str,
        name: str,
        asset_type: str,
        location: str,
    ) -> Asset:
        asset = Asset(
            asset_id=asset_id,
            tenant_id=tenant_id,
            name=name,
            asset_type=asset_type,
            location=location,
        )
        return self.repository.save(asset)

    def get_asset(self, asset_id: str) -> Asset:
        asset = self.repository.get_by_id(asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")
        return asset

    def list_assets(self, tenant_id: str) -> list[Asset]:
        return self.repository.list_by_tenant(tenant_id)

    def update_status(self, asset_id: str, status: str) -> Asset:
        asset = self.get_asset(asset_id)
        if status == "flagged":
            asset.flag()
        elif status == "disabled":
            asset.deactivate()
        elif status == "active":
            asset.reactivate()
        else:
            raise ValueError(f"Invalid status: {status}")
        return self.repository.update(asset)
