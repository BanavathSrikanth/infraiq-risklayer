from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


@dataclass
class Decision:
    decision_id: str
    asset_id: str
    tenant_id: str
    recommendation_id: str
    outcome: Literal["approved", "rejected", "modified", "accepted", "deferred"] = "approved"
    decided_by: str = ""
    rationale: str = ""
    conditions: list[str] | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    @property
    def approved(self) -> bool:
        return self.outcome in {"approved", "accepted"}
