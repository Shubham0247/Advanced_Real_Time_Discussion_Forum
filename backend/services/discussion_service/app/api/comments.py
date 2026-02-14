from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from backend.shared.database.session import get_db
from backend.services.auth_service.app.core.security import get_current_user
from backend.services.discussion_service.app.services.comment_service import CommentService
from backend.services.discussion_service.app.schemas.comment import (
    CommentCreate,
    CommentRead,
    CommentSearchResponse,
    CommentUpdate,
)


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/thread/{thread_id}", response_model=CommentRead)
def create_comment(
    thread_id: UUID,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CommentService(db)
    return service.create_comment(
        thread_id=thread_id,
        content=comment_data.content,
        author_id=current_user.id,
        parent_id=comment_data.parent_id,
    )


@router.get("/thread/{thread_id}", response_model=list[CommentRead])
def get_thread_comments(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = CommentService(db)
    return service.get_thread_comments(thread_id, current_user)


@router.get("/search", response_model=CommentSearchResponse)
def search_comments(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = CommentService(db)
    return service.search_comments(q, page, size, current_user)


@router.patch("/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: UUID,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CommentService(db)
    return service.update_comment(
        comment_id,
        comment_data.content,
        current_user,
    )


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CommentService(db)
    service.delete_comment(comment_id, current_user)
    return {"message": "Comment deleted successfully"}
