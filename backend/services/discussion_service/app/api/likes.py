from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from backend.shared.database.session import get_db
from backend.services.auth_service.app.core.security import get_current_user
from backend.services.discussion_service.app.services.like_service import LikeService
from backend.services.discussion_service.app.schemas.like import ThreadLikersResponse

router = APIRouter(prefix="/likes", tags=["Likes"])

@router.post("/thread/{thread_id}")
def toggle_thread_like(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = LikeService(db)
    return service.toggle_thread_like(thread_id, current_user.id)

@router.post("/comment/{comment_id}")
def toggle_comment_like(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = LikeService(db)
    return service.toggle_comment_like(comment_id, current_user.id)


@router.get("/thread/{thread_id}/users", response_model=ThreadLikersResponse)
def list_thread_likers(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = LikeService(db)
    return service.list_thread_likers(thread_id)

