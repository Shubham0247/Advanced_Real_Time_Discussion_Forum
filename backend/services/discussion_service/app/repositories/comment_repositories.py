from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from backend.services.discussion_service.app.models.comment import Comment


class CommentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_by_id(self, comment_id: UUID) -> Comment | None:
        query = select(Comment).where(Comment.id == comment_id)
        return self.db.scalar(query)

    def get_thread_comments(self, thread_id: UUID) -> List[Comment]:
        query = select(Comment).where(
            Comment.thread_id == thread_id
        )
        return list(self.db.scalars(query))

    def list_comments(self, skip: int, limit: int) -> List[Comment]:
        query = (
            select(Comment)
            .where(Comment.is_deleted == False)
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(query))

    def count_comments(self) -> int:
        query = select(func.count()).select_from(Comment).where(Comment.is_deleted == False)
        return self.db.scalar(query)

    def search_comments(self, keyword: str, skip: int, limit: int) -> List[Comment]:
        pattern = f"%{keyword.strip()}%"
        query = (
            select(Comment)
            .where(
                Comment.is_deleted == False,
                Comment.content.ilike(pattern),
            )
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(query))

    def count_search_comments(self, keyword: str) -> int:
        pattern = f"%{keyword.strip()}%"
        query = select(func.count()).select_from(Comment).where(
            Comment.is_deleted == False,
            Comment.content.ilike(pattern),
        )
        return self.db.scalar(query)

    def update(self, comment: Comment) -> Comment:
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def soft_delete(self, comment: Comment):
        comment.is_deleted = True
        self.db.commit()
