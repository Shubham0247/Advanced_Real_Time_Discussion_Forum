from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.services.discussion_service.app.models.thread_report import ThreadReport
from backend.services.discussion_service.app.repositories.report_repository import ReportRepository
from backend.services.discussion_service.app.services.thread_service import ThreadService


class ReportService:
    VALID_STATUSES = {"reported", "pending", "approved"}

    def __init__(self, db: Session):
        """Initialize the report service with repository and thread dependencies."""
        self.db = db
        self.repo = ReportRepository(db)
        self.thread_service = ThreadService(db)

    def report_thread(self, thread_id: UUID, reporter_id: UUID, reason: str | None = None):
        """Create a report for a thread and mark the thread as reported."""
        thread = self.thread_service.get_thread(thread_id)
        if thread.author_id == reporter_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot report your own thread",
            )

        existing = self.repo.get_by_thread_and_reporter(thread_id, reporter_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reported this thread",
            )

        report = ThreadReport(
            thread_id=thread_id,
            reporter_id=reporter_id,
            reason=(reason or "").strip() or None,
            status="reported",
        )
        created = self.repo.create(report)
        # Reported threads should surface in moderation "Reported".
        self.thread_service.update_moderation_status(thread_id, "reported")
        return created

    def list_reports(self, *, status_filter: str, q: str | None, page: int, size: int):
        """Return paginated reports filtered by status and optional query."""
        status_value = (status_filter or "reported").strip().lower()
        if status_value not in self.VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter",
            )

        skip = (page - 1) * size
        rows = self.repo.list_reports(status=status_value, q=q, skip=skip, limit=size)
        total = self.repo.count_reports(status=status_value, q=q)

        items = [
            {
                "id": report.id,
                "thread_id": report.thread_id,
                "thread_title": thread_title,
                "thread_author_id": thread_author_id,
                "reporter_id": report.reporter_id,
                "reporter_username": reporter_username,
                "reporter_name": reporter_name,
                "reason": report.reason,
                "status": report.status,
                "created_at": report.created_at,
            }
            for report, thread_title, thread_author_id, reporter_username, reporter_name in rows
        ]

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": items,
        }

    def update_report_status(self, report_id: UUID, status_value: str):
        """Update the status of a report after validating allowed values."""
        status_value = status_value.strip().lower()
        if status_value not in self.VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value",
            )

        report = self.repo.get_by_id(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )

        report.status = status_value
        return self.repo.update(report)
