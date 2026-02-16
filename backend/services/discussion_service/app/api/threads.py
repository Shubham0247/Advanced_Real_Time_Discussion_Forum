from pathlib import Path
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, Request
from sqlalchemy.orm import Session

from backend.shared.database.session import get_db
from backend.services.discussion_service.app.services.thread_service import ThreadService
from backend.services.discussion_service.app.services.activity_service import ActivityService
from backend.services.discussion_service.app.services.report_service import ReportService
from backend.services.discussion_service.app.schemas.thread import (
    ThreadCreate,
    ThreadRead,
    ThreadUpdate,
    ThreadListResponse,
)
from backend.services.discussion_service.app.schemas.activity import UserActivityListResponse
from backend.services.discussion_service.app.schemas.report import ThreadReportCreate
from backend.services.auth_service.app.core.security import get_current_user


router = APIRouter(prefix="/threads", tags=["Threads"])

THREAD_IMAGE_UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "threads"
THREAD_IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
        image_url=thread_data.image_url,
        author_id=current_user.id,
    )


@router.post("/upload-image")
def upload_thread_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    extension = Path(file.filename or "").suffix.lower() or ".png"
    if extension not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    data = file.file.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size must be <= 8MB")

    filename = f"{current_user.id}_{uuid4().hex}{extension}"
    filepath = THREAD_IMAGE_UPLOAD_DIR / filename
    with filepath.open("wb") as f:
        f.write(data)

    image_url = f"{str(request.base_url).rstrip('/')}/uploads/threads/{filename}"
    return {"image_url": image_url}
 
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


@router.get("/me", response_model=ThreadListResponse)
def my_threads(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ThreadService(db)
    return service.list_my_threads(page, size, current_user)


@router.get("/me/activity", response_model=UserActivityListResponse)
def my_activity(
    range: str = Query("all", pattern="^(24h|7d|1m|all)$"),
    activity_type: str = Query("all", alias="type", pattern="^(all|like|comment)$"),
    page: int = Query(1, ge=1),
    size: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ActivityService(db)
    return service.list_my_activity(
        user_id=current_user.id,
        range_key=range,
        type_key=activity_type,
        page=page,
        size=size,
    )

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


@router.post("/{thread_id}/report")
def report_thread(
    thread_id: UUID,
    payload: ThreadReportCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    report = service.report_thread(
        thread_id=thread_id,
        reporter_id=current_user.id,
        reason=payload.reason,
    )
    return {"message": "Thread reported successfully", "report_id": str(report.id)}
