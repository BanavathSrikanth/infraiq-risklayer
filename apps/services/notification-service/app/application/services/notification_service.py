from app.domain.entities.notification import Notification
from app.infrastructure.repositories.notification_repository import NotificationRepository


class NotificationApplicationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def send_notification(
        self,
        notification_id: str,
        tenant_id: str,
        asset_id: str,
        message: str,
    ) -> Notification:
        notification = Notification(
            notification_id=notification_id,
            tenant_id=tenant_id,
            asset_id=asset_id,
            message=message,
        )
        return self.repository.save(notification)

    def list_notifications(self, tenant_id: str) -> list[Notification]:
        return self.repository.list_by_tenant(tenant_id)
