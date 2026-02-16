from uuid import UUID, uuid4
from pathlib import Path
from sqlalchemy import select, func
from backend.services.auth_service.app.models.user import User
from backend.services.auth_service.app.models.role import Role
from backend.shared.database.session import get_db
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from backend.services.auth_service.app.schemas.user import (
    ChangePasswordRequest,
    MentionResolveRequest,
    MentionResolveResponse,
    MentionSuggestResponse,
    UserSearchResponse,
    UserListResponse,
    UserRead,
    UserStatusUpdate,
    UserUpdate,
)
from backend.services.auth_service.app.core.security import get_current_user
from backend.services.auth_service.app.core.security import require_roles
from backend.services.auth_service.app.repositories.user_repository import UserRepository
from backend.services.auth_service.app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
AVATAR_UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "avatars"
AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/me", response_model=UserRead)
def get_me(current_user = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user.
    """
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    current_user = _current_user
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password")
def change_my_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    current_user = _current_user
    user_service = UserService(db)
    try:
        user_service.change_password(
            current_user,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "Password changed successfully"}


@router.post("/me/deactivate")
def deactivate_my_account(
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    current_user = _current_user
    current_user.is_active = False
    db.commit()
    return {"message": "Account deactivated successfully"}


@router.get("/mentions/suggest", response_model=MentionSuggestResponse)
def suggest_mentions(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    _ = _current_user
    user_repo = UserRepository(db)
    users = user_repo.list_users(skip=0, limit=limit, q=q)
    active_users = [u for u in users if u.is_active]
    return {"items": active_users}


@router.get("/search", response_model=UserSearchResponse)
def search_users(
    q: str = Query(..., min_length=1, max_length=100),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    _ = _current_user
    user_repo = UserRepository(db)
    skip = (page - 1) * size
    items = user_repo.search_public_users(skip=skip, limit=size, q=q)
    total = user_repo.count_public_users(q=q)
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items,
    }


@router.post("/mentions/resolve", response_model=MentionResolveResponse)
def resolve_mentions(
    payload: MentionResolveRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    _ = _current_user
    normalized = {
        username.strip().lstrip("@").lower()
        for username in payload.usernames
        if username and username.strip()
    }
    if not normalized:
        return {"existing_usernames": []}

    rows = list(
        db.execute(
            select(User.username).where(func.lower(User.username).in_(normalized))
        ).scalars()
    )
    return {"existing_usernames": rows}


@router.post("/me/avatar", response_model=UserRead)
def upload_me_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    current_user = _current_user
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    extension = Path(file.filename or "").suffix.lower() or ".png"
    if extension not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    data = file.file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size must be <= 5MB")

    filename = f"{current_user.id}_{uuid4().hex}{extension}"
    filepath = AVATAR_UPLOAD_DIR / filename
    with filepath.open("wb") as f:
        f.write(data)

    base_url = str(request.base_url).rstrip("/")
    current_user.avatar_url = f"{base_url}/uploads/avatars/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/admin/list", response_model=UserListResponse)
def list_users_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None),
    role: str | None = Query(None),
    db: Session = Depends(get_db),
    _current_user = Depends(require_roles(["admin"])),
):
    _ = _current_user
    user_repo = UserRepository(db)
    skip = (page - 1) * size
    items = user_repo.list_users(skip=skip, limit=size, q=q, role=role)
    total = user_repo.count_users(q=q, role=role)
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items,
    }


@router.patch("/{user_id}/status")
def update_user_status(
    user_id: UUID,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    _current_user = Depends(require_roles(["admin"])),
):
    _ = _current_user
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = status_data.is_active
    db.commit()
    db.refresh(user)

    state = "activated" if user.is_active else "deactivated"
    return {
        "message": f"User {state} successfully",
        "user_id": str(user.id),
        "is_active": user.is_active,
    }


@router.post("/{user_id}/promote")
def promote_user(
    user_id: UUID,
    role_name: str,
    db: Session = Depends(get_db),
    _current_user = Depends(require_roles(["admin"]))
):
    """
    Promote a user to a specific role (Admin only)
    """

    _ = _current_user
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.execute(
        select(Role).where(Role.name == role_name)
    ).scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role in user.roles:
        return {"message": "User already has this role"}

    user.roles.append(role)
    db.commit()

    return {"message": f"User promoted to {role_name}"}


@router.post("/{user_id}/demote")
def demote_user(
    user_id: UUID,
    role_name: str,
    db: Session = Depends(get_db),
    _current_user = Depends(require_roles(["admin"]))
):
    """
    Demote a user from a specific role (Admin only)
    """

    _ = _current_user
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.execute(
        select(Role).where(Role.name == role_name)
    ).scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role not in user.roles:
        return {"message": "User does not have this role"}

    user.roles.remove(role)
    db.commit()

    return {"message": f"User demoted from {role_name}"}
