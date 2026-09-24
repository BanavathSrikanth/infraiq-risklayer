from app.domain.entities.tenant import Tenant
from app.infrastructure.repositories.tenant_repository import TenantRepository


class TenantApplicationService:
    def __init__(self, repository: TenantRepository):
        self.repository = repository

    def create_tenant(self, tenant_id: str, name: str) -> Tenant:
        tenant = Tenant(tenant_id=tenant_id, name=name)
        return self.repository.save(tenant)

    def get_tenant(self, tenant_id: str) -> Tenant:
        tenant = self.repository.get_by_id(tenant_id)
        if tenant is None:
            raise ValueError(f"Tenant {tenant_id} not found")
        return tenant

    def grant_role(self, tenant_id: str, role: str) -> Tenant:
        tenant = self.get_tenant(tenant_id)
        tenant.add_role(role)
        return self.repository.update(tenant)

    def authorize(self, tenant_id: str, required_roles: list[str]) -> bool:
        tenant = self.get_tenant(tenant_id)
        return tenant.is_authorized(required_roles)
