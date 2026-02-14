from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import List

class ThreadBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=1)

class ThreadCreate(ThreadBase):
    pass

class ThreadUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = Field(None, min_length=1)
    is_locked: bool | None = None

class ThreadRead(ThreadBase):
    id: UUID
    author_id: UUID
    author_username: str | None = None
    author_name: str | None = None
    author_avatar: str | None = None
    is_deleted: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    like_count: int
    is_liked_by_current_user: bool

    model_config = ConfigDict(from_attributes=True)

class ThreadListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ThreadRead]