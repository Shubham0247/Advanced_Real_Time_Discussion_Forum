from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ThreadReportCreate(BaseModel):
    reason: str | None = Field(None, max_length=500)


class ThreadReportRead(BaseModel):
    id: UUID
    thread_id: UUID
    thread_title: str
    thread_author_id: UUID
    reporter_id: UUID
    reporter_username: str
    reporter_name: str | None = None
    reason: str | None = None
    status: str
    created_at: datetime


class ThreadReportListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[ThreadReportRead]


class ThreadReportStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(reported|pending|approved)$")
