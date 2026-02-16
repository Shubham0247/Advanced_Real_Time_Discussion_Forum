from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import List


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    parent_id: UUID | None = None


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentRead(BaseModel):
    id: UUID
    content: str
    thread_id: UUID
    author_id: UUID
    author_username: str | None = None
    author_name: str | None = None
    author_avatar: str | None = None
    parent_id: UUID | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    like_count: int = 0
    is_liked_by_current_user: bool = False
    replies: List["CommentRead"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


CommentRead.model_rebuild()


class CommentSearchResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[CommentRead]
