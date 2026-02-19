from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.services.discussion_service.app.repositories.activity_repository import (
    ActivityRepository,
)


class ActivityService:
    VALID_RANGES = {"24h", "7d", "1m", "all"}
    VALID_TYPES = {"all", "like", "comment"}

    def __init__(self, db: Session):
        """Initialize the activity service with its repository dependency."""
        self.repo = ActivityRepository(db)

    def list_my_activity(
        self,
        *,
        user_id: UUID,
        range_key: str,
        type_key: str,
        page: int,
        size: int,
    ):
        """Return paginated user activity filtered by time range and type."""
        normalized = (range_key or "all").strip().lower()
        if normalized not in self.VALID_RANGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid range filter",
            )
        normalized_type = (type_key or "all").strip().lower()
        if normalized_type not in self.VALID_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type filter",
            )

        skip = (page - 1) * size
        items = self.repo.list_user_activity(
            user_id=user_id,
            range_key=normalized,
            type_key=normalized_type,
            skip=skip,
            limit=size,
        )
        total = self.repo.count_user_activity(
            user_id=user_id,
            range_key=normalized,
            type_key=normalized_type,
        )
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": items,
        }
