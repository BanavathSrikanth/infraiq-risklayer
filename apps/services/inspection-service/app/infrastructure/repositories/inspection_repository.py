from typing import Dict, List, Optional

from app.domain.entities.inspection import Inspection


class InspectionRepository:
    def __init__(self):
        self._store: Dict[str, Inspection] = {}

    def save(self, inspection: Inspection) -> Inspection:
        self._store[inspection.inspection_id] = inspection
        return inspection

    def get_by_id(self, inspection_id: str) -> Optional[Inspection]:
        return self._store.get(inspection_id)

    def list_by_tenant(self, tenant_id: str, asset_id: str | None = None) -> List[Inspection]:
        records = [item for item in self._store.values() if item.tenant_id == tenant_id]
        if asset_id:
            records = [item for item in records if item.asset_id == asset_id]
        return records

    def update(self, inspection: Inspection) -> Inspection:
        self._store[inspection.inspection_id] = inspection
        return inspection
