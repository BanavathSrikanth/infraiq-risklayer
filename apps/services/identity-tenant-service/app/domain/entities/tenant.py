from dataclasses import dataclass, field
from typing import List


@dataclass
class Tenant:
    tenant_id: str
    name: str
    status: str = "active"
    roles: List[str] = field(default_factory=list)

    def add_role(self, role: str) -> None:
        if role not in self.roles:
            self.roles.append(role)

    def is_authorized(self, required_roles: list[str]) -> bool:
        return any(role in self.roles for role in required_roles)
