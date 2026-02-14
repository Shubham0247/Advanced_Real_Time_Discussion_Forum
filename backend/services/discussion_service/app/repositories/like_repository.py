from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID

from backend.services.discussion_service.app.models.like import Like

class LikeRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, like: Like) -> Like:
        self.db.add(like)
        self.db.commit()
        self.db.refresh(like)
        return like

    def delete(self, like: Like):
        self.db.delete(like)
        self.db.commit()
    
    def get_thread_like(self, user_id: UUID, thread_id: UUID):
        query = select(Like).where(
            Like.user_id == user_id,
            Like.thread_id == thread_id
        )
        return self.db.scalar(query)
    
    def get_comment_like(self, user_id: UUID, comment_id: UUID):
        query = select(Like).where(
            Like.user_id == user_id,
            Like.comment_id == comment_id
        )
        return self.db.scalar(query)
    
    def count_thread_likes(self, thread_id: UUID) -> int:
        query = select(func.count()).where(Like.thread_id == thread_id)
        return self.db.scalar(query)
    
    def count_comment_likes(self, comment_id: UUID) -> int:
        query = select(func.count()).where(Like.comment_id == comment_id)
        return self.db.scalar(query)
    
    def is_thread_liked_by_user(self, thread_id: UUID, user_id: UUID) -> bool:
        query = select(Like).where(
            Like.thread_id == thread_id,
            Like.user_id == user_id
        )
        return self.db.scalar(query) is not None
    
    def is_comment_liked_by_user(self, comment_id: UUID, user_id: UUID) -> bool:
        query = select(Like).where(
            Like.comment_id == comment_id,
            Like.user_id == user_id
        )
        return self.db.scalar(query) is not None