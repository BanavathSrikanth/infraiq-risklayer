from dataclasses import dataclass


@dataclass
class Asset:
    asset_id: str
    tenant_id: str
    name: str
    asset_type: str
    location: str
    status: str = "active"

    def flag(self) -> None:
        self.status = "flagged"

    def deactivate(self) -> None:
        self.status = "disabled"

    def reactivate(self) -> None:
        self.status = "active"
