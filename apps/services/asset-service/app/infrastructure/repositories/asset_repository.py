from typing import Dict, List, Optional

from app.domain.entities.asset import Asset


class AssetRepository:
    def __init__(self):
        self._store: Dict[str, Asset] = {}

    def save(self, asset: Asset) -> Asset:
        self._store[asset.asset_id] = asset
        return asset

    def get_by_id(self, asset_id: str) -> Optional[Asset]:
        return self._store.get(asset_id)

    def list_by_tenant(self, tenant_id: str) -> List[Asset]:
        return [asset for asset in self._store.values() if asset.tenant_id == tenant_id]

    def update(self, asset: Asset) -> Asset:
        self._store[asset.asset_id] = asset
        return asset
