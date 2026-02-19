from uuid import UUID

from fastapi import HTTPException, status

from backend.services.notification_service.app.repositories.notification_repositories import NotificationRepository


class NotificationService:
    def __init__(self, db):
        """Initialize the notification service with its repository dependency."""
        self.repo = NotificationRepository(db)

    def list_my_notifications(self, user_id: UUID, page: int, size: int):
        """Return paginated notifications for a user."""
        skip = (page - 1) * size
        items = self.repo.list_user_notifications(user_id, skip=skip, limit=size)
        total = self.repo.count_user_notifications(user_id)
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": items,
        }

    def unread_count(self, user_id: UUID) -> int:
        """Return the unread notification count for a user."""
        return self.repo.count_unread_notifications(user_id)

    def mark_one_read(self, notification_id: UUID, user_id: UUID):
        """Mark a specific user notification as read."""
        notification = self.repo.get_user_notification_by_id(notification_id, user_id)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        return self.repo.mark_as_read(notification)

    def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user and return affected count."""
        return self.repo.mark_all_as_read(user_id)
