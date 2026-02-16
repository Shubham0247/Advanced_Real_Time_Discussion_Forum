from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UserActivityRead(BaseModel):
    activity_type: str
    thread_id: UUID | None = None
    comment_id: UUID | None = None
    title: str | None = None
    preview: str | None = None
    created_at: datetime


class UserActivityListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserActivityRead]
