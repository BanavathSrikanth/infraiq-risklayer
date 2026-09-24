from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Report:
    report_id: str
    asset_id: str
    tenant_id: str
    report_type: str
    status: str
    generated_at: datetime

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now(timezone.utc)
