from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Finding:
    finding_id: str
    asset_id: str
    tenant_id: str
    inspection_id: str
    finding_type: str
    description: str
    severity: str = "unknown"
    identified_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
