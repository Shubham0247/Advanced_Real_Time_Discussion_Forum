from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    id: UUID
    user_id: UUID
    actor_id: UUID
    type: str
    reference_id: UUID
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[NotificationRead]


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int
