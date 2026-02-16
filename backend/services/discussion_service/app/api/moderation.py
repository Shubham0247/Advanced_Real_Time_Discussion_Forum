from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.services.auth_service.app.core.security import require_roles
from backend.services.discussion_service.app.schemas.comment import CommentSearchResponse
from backend.services.discussion_service.app.schemas.report import (
    ThreadReportListResponse,
    ThreadReportStatusUpdate,
)
from backend.services.discussion_service.app.schemas.thread import ThreadListResponse
from backend.services.discussion_service.app.services.comment_service import CommentService
from backend.services.discussion_service.app.services.report_service import ReportService
from backend.services.discussion_service.app.services.thread_service import ThreadService
from backend.shared.database.session import get_db
from pydantic import BaseModel, Field

router = APIRouter(prefix="/moderation", tags=["Moderation"])


class ThreadModerationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|reported|approved)$")


@router.get("/threads", response_model=ThreadListResponse)
def moderation_threads(
    status: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "moderator"])),
):
    service = ThreadService(db)
    status_value = status.strip().lower() if isinstance(status, str) and status.strip() else None
    if q and q.strip():
        if status_value is None:
            return service.search_threads(q, page, size, current_user)
        return service.search_threads(
            q,
            page,
            size,
            current_user,
            moderation_status=status_value,
        )
    if status_value is None:
        return service.list_threads(page, size, current_user)
    return service.list_threads(
        page,
        size,
        current_user,
        moderation_status=status_value,
    )


@router.get("/comments", response_model=CommentSearchResponse)
def moderation_comments(
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "moderator"])),
):
    service = CommentService(db)
    if q and q.strip():
        return service.search_comments(q, page, size, current_user)
    return service.list_comments(page, size, current_user)


@router.get("/reports", response_model=ThreadReportListResponse)
def moderation_reports(
    status: str = Query("reported"),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "moderator"])),
):
    service = ReportService(db)
    return service.list_reports(status_filter=status, q=q, page=page, size=size)


@router.patch("/reports/{report_id}/status")
def update_report_status(
    report_id: UUID,
    payload: ThreadReportStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "moderator"])),
):
    service = ReportService(db)
    updated = service.update_report_status(report_id, payload.status)
    return {"message": "Report status updated", "report_id": str(updated.id), "status": updated.status}


@router.patch("/threads/{thread_id}/status")
def update_thread_moderation_status(
    thread_id: UUID,
    payload: ThreadModerationStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "moderator"])),
):
    service = ThreadService(db)
    updated = service.update_moderation_status(thread_id, payload.status)
    return {"message": "Thread moderation status updated", "thread_id": str(updated.id), "status": updated.moderation_status}
