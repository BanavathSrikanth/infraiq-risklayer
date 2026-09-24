from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Notification:
    notification_id: str
    tenant_id: str
    asset_id: str
    message: str
    sent_at: datetime | None = None

    def __post_init__(self):
        if self.sent_at is None:
            self.sent_at = datetime.now(timezone.utc)
