from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.services.auth_service.app.core.security import get_current_user
from backend.services.notification_service.app.schemas.notification import (
    NotificationListResponse,
    NotificationRead,
    NotificationUnreadCountResponse,
)
from backend.services.notification_service.app.services.notification_service import NotificationService
from backend.shared.database.session import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=NotificationListResponse)
def list_my_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)
    return service.list_my_notifications(current_user.id, page, size)


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
def unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)
    return {"unread_count": service.unread_count(current_user.id)}


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_one_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)
    return service.mark_one_read(notification_id, current_user.id)


@router.patch("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)
    updated = service.mark_all_read(current_user.id)
    return {"message": "Notifications marked as read", "updated_count": updated}
