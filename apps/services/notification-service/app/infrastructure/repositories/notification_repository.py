from typing import Dict, List

from app.domain.entities.notification import Notification


class NotificationRepository:
    def __init__(self):
        self._store: Dict[str, Notification] = {}

    def save(self, notification: Notification) -> Notification:
        self._store[notification.notification_id] = notification
        return notification

    def list_by_tenant(self, tenant_id: str) -> List[Notification]:
        return [item for item in self._store.values() if item.tenant_id == tenant_id]
