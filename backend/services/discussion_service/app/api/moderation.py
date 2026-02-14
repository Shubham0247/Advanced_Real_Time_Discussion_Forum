from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.services.auth_service.app.core.security import require_roles
from backend.services.discussion_service.app.schemas.comment import CommentSearchResponse
from backend.services.discussion_service.app.schemas.thread import ThreadListResponse
from backend.services.discussion_service.app.services.comment_service import CommentService
from backend.services.discussion_service.app.services.thread_service import ThreadService
from backend.shared.database.session import get_db

router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.get("/threads", response_model=ThreadListResponse)
def moderation_threads(
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "moderator"])),
):
    service = ThreadService(db)
    if q and q.strip():
        return service.search_threads(q, page, size, current_user)
    return service.list_threads(page, size, current_user)


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
