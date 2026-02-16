from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from typing import List
from uuid import UUID

from backend.services.discussion_service.app.models.thread import Thread

class ThreadRepository:
    """
    Handles database operations related to threads.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, thread: Thread) -> Thread:
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        return thread
    
    def get_by_id(self, thread_id: UUID) -> Thread | None:
        query = select(Thread).where(
            Thread.id == thread_id,
            Thread.is_deleted == False
        )
        return self.db.scalar(query)
    
    def list_threads(self, skip: int, limit: int, moderation_status: str | None = None) -> List[Thread]:
        filters = [Thread.is_deleted == False]
        if moderation_status:
            filters.append(Thread.moderation_status == moderation_status)
        query = (
            select(Thread)
            .where(*filters)
            .order_by(Thread.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(query))
    
    def count_threads(self, moderation_status: str | None = None) -> int:
        filters = [Thread.is_deleted == False]
        if moderation_status:
            filters.append(Thread.moderation_status == moderation_status)
        query = select(func.count()).select_from(Thread).where(*filters)
        return self.db.scalar(query)

    def search_threads(
        self,
        keyword: str,
        skip: int,
        limit: int,
        moderation_status: str | None = None,
    ) -> List[Thread]:
        pattern = f"%{keyword.strip()}%"
        filters = [Thread.is_deleted == False]
        if moderation_status:
            filters.append(Thread.moderation_status == moderation_status)
        query = (
            select(Thread)
            .where(
                *filters,
                or_(
                    Thread.title.ilike(pattern),
                    Thread.description.ilike(pattern),
                ),
            )
            .order_by(Thread.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(query))

    def count_search_threads(self, keyword: str, moderation_status: str | None = None) -> int:
        pattern = f"%{keyword.strip()}%"
        filters = [Thread.is_deleted == False]
        if moderation_status:
            filters.append(Thread.moderation_status == moderation_status)
        query = select(func.count()).select_from(Thread).where(
            *filters,
            or_(
                Thread.title.ilike(pattern),
                Thread.description.ilike(pattern),
            ),
        )
        return self.db.scalar(query)

    def list_threads_by_author(self, author_id: UUID, skip: int, limit: int) -> List[Thread]:
        query = (
            select(Thread)
            .where(
                Thread.is_deleted == False,
                Thread.author_id == author_id,
            )
            .order_by(Thread.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(query))

    def count_threads_by_author(self, author_id: UUID) -> int:
        query = select(func.count()).select_from(Thread).where(
            Thread.is_deleted == False,
            Thread.author_id == author_id,
        )
        return self.db.scalar(query)
    
    def update(self, thread: Thread) -> Thread:
        self.db.commit()
        self.db.refresh(thread)
        return thread
    
    def soft_delete(self, thread: Thread) -> None:
        thread.is_deleted = True
        self.db.commit()