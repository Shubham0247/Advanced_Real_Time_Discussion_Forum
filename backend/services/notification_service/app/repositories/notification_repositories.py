from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from backend.services.notification_service.app.models.notification import Notification


class NotificationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(self, user_id: UUID) -> List[Notification]:
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(query))

    def list_user_notifications(self, user_id: UUID, *, skip: int, limit: int) -> List[Notification]:
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(query))

    def count_user_notifications(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        return self.db.scalar(query)

    def count_unread_notifications(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        return self.db.scalar(query)

    def get_user_notification_by_id(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        return self.db.scalar(query)

    def mark_as_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: UUID) -> int:
        notifications = list(
            self.db.scalars(
                select(Notification).where(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
            )
        )
        for notification in notifications:
            notification.is_read = True
        self.db.commit()
        return len(notifications)
