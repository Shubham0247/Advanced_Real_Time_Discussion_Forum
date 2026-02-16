from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from backend.services.discussion_service.app.models.thread import Thread
from backend.services.discussion_service.app.models.thread_report import ThreadReport
from backend.services.auth_service.app.models.user import User


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_thread_and_reporter(self, thread_id: UUID, reporter_id: UUID) -> ThreadReport | None:
        query = select(ThreadReport).where(
            ThreadReport.thread_id == thread_id,
            ThreadReport.reporter_id == reporter_id,
        )
        return self.db.scalar(query)

    def create(self, report: ThreadReport) -> ThreadReport:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_id(self, report_id: UUID) -> ThreadReport | None:
        query = select(ThreadReport).where(ThreadReport.id == report_id)
        return self.db.scalar(query)

    def update(self, report: ThreadReport) -> ThreadReport:
        self.db.commit()
        self.db.refresh(report)
        return report

    def list_reports(self, *, status: str, q: str | None, skip: int, limit: int):
        query = (
            select(
                ThreadReport,
                Thread.title,
                Thread.author_id,
                User.username,
                User.full_name,
            )
            .join(Thread, Thread.id == ThreadReport.thread_id)
            .join(User, User.id == ThreadReport.reporter_id)
            .where(
                ThreadReport.status == status,
                Thread.is_deleted == False,
            )
        )

        if q:
            pattern = f"%{q.strip()}%"
            query = query.where(
                or_(
                    Thread.title.ilike(pattern),
                    User.username.ilike(pattern),
                    User.full_name.ilike(pattern),
                    ThreadReport.reason.ilike(pattern),
                )
            )

        query = (
            query.order_by(ThreadReport.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(query).all())

    def count_reports(self, *, status: str, q: str | None) -> int:
        query = (
            select(func.count())
            .select_from(ThreadReport)
            .join(Thread, Thread.id == ThreadReport.thread_id)
            .join(User, User.id == ThreadReport.reporter_id)
            .where(
                ThreadReport.status == status,
                Thread.is_deleted == False,
            )
        )

        if q:
            pattern = f"%{q.strip()}%"
            query = query.where(
                or_(
                    Thread.title.ilike(pattern),
                    User.username.ilike(pattern),
                    User.full_name.ilike(pattern),
                    ThreadReport.reason.ilike(pattern),
                )
            )
        return self.db.scalar(query)
