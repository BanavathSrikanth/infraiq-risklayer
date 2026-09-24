from typing import Dict, Optional

from app.domain.entities.tenant import Tenant


class TenantRepository:
    def __init__(self):
        self._store: Dict[str, Tenant] = {}

    def save(self, tenant: Tenant) -> Tenant:
        self._store[tenant.tenant_id] = tenant
        return tenant

    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self._store.get(tenant_id)

    def update(self, tenant: Tenant) -> Tenant:
        self._store[tenant.tenant_id] = tenant
        return tenant
