from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from backend.shared.database.session import get_db
from backend.services.discussion_service.app.services.thread_service import ThreadService
from backend.services.discussion_service.app.schemas.thread import (
    ThreadCreate,
    ThreadRead,
    ThreadUpdate,
    ThreadListResponse,
)
from backend.services.auth_service.app.core.security import get_current_user


router = APIRouter(prefix="/threads", tags=["Threads"])

@router.post("/", response_model=ThreadRead)
def create_thread(
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = ThreadService(db)
    return service.create_thread(
        title = thread_data.title,
        description=thread_data.description,
        author_id=current_user.id,
    )
 
@router.get("/", response_model=ThreadListResponse)
def list_threads(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = ThreadService(db)
    return service.list_threads(page, size, current_user)


@router.get("/search", response_model=ThreadListResponse)
def search_threads(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = ThreadService(db)
    return service.search_threads(q, page, size, current_user)

@router.get("/{thread_id}", response_model=ThreadRead)
def get_thread(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = ThreadService(db)
    return service.get_thread(thread_id, current_user)

@router.patch("/{thread_id}", response_model=ThreadRead)
def update_thread(
    thread_id: UUID,
    thread_data: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = ThreadService(db)
    return service.update_thread(
        thread_id,
        thread_data.model_dump(exclude_unset=True),
        current_user,
    )

@router.delete("/{thread_id}")
def delete_thread(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = ThreadService(db)
    service.delete_thread(thread_id, current_user)
    return {"message": "Thread deleted successfully"}
