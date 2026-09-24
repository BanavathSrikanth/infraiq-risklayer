from fastapi import APIRouter, Depends, HTTPException

from app.application.services.notification_service import NotificationApplicationService
from app.infrastructure.repositories.notification_repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_service() -> NotificationApplicationService:
    return NotificationApplicationService(NotificationRepository())


@router.post("")
async def send_notification(
    payload: dict,
    service: NotificationApplicationService = Depends(get_notification_service),
):
    try:
        notification = service.send_notification(
            notification_id=payload["notification_id"],
            tenant_id=payload["tenant_id"],
            asset_id=payload["asset_id"],
            message=payload["message"],
        )
        return {
            "notification_id": notification.notification_id,
            "tenant_id": notification.tenant_id,
            "asset_id": notification.asset_id,
            "message": notification.message,
            "sent_at": notification.sent_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
