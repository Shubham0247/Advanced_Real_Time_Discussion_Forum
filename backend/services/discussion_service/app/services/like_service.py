from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.services.discussion_service.app.models.like import Like
from backend.services.discussion_service.app.repositories.like_repository import LikeRepository
from backend.services.discussion_service.app.services.thread_service import ThreadService
from backend.services.discussion_service.app.repositories.comment_repositories import CommentRepository
from backend.services.discussion_service.app.core.events import publish_event

class LikeService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = LikeRepository(db)
        self.thread_service = ThreadService(db)
        self.comment_repo = CommentRepository(db)

    def toggle_thread_like(self, thread_id: UUID, user_id: UUID):

        thread = self.thread_service.get_thread(thread_id)
        existing = self.repo.get_thread_like(user_id, thread_id)

        if existing:
            self.repo.delete(existing)
            count = self.repo.count_thread_likes(thread_id)

            publish_event(
                channel="thread_updates",
                thread_id=str(thread_id),
                actor_id=str(user_id),
                event="thread.like.updated",
                payload={
                    "thread_id": str(thread_id),
                    "like_count": count
                }
            )

            return {
                "liked": False,
                "liked_count": count
    }

        
        try:
            like = Like(user_id=user_id, thread_id=thread_id)
            self.repo.create(like)
            count = self.repo.count_thread_likes(thread_id)

            publish_event(
                channel="thread_updates",
                thread_id=str(thread_id),
                actor_id=str(user_id),
                event="thread.like.updated",
                payload={
                    "thread_id": str(thread_id),
                    "like_count": count
                }
            )

            publish_event(
                channel="discussion_events",
                event="thread.liked",
                thread_id=str(thread_id),
                actor_id=str(user_id),
                payload={
                    "owner_id": str(thread.author_id)
                }
            )


            return {
                "liked": True,
                "liked_count": count
                }
        
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already liked",
            )
        
    def toggle_comment_like(self, comment_id: UUID, user_id: UUID):
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        existing = self.repo.get_comment_like(user_id, comment_id)

        if existing:
            self.repo.delete(existing)
            count = self.repo.count_comment_likes(comment_id)

            publish_event(
                channel="thread_updates",
                thread_id=str(comment.thread_id),
                actor_id=str(user_id),
                event="comment.like.updated",
                payload={
                    "comment_id": str(comment_id),
                    "like_count": count
                }
            )

            return {
                "liked": False,
                "liked_count": count
            }


        try:
            like = Like(user_id=user_id, comment_id=comment_id)
            self.repo.create(like)
            count = self.repo.count_comment_likes(comment_id)

            publish_event(
                channel="thread_updates",
                thread_id=str(comment.thread_id),
                actor_id=str(user_id),
                event="comment.like.updated",
                payload={
                    "comment_id": str(comment_id),
                    "like_count": count
                }
            )

            publish_event(
                channel="discussion_events",
                event="comment.liked",
                thread_id=str(comment.thread_id),
                actor_id=str(user_id),
                payload={
                    "owner_id": str(comment.author_id),
                    "comment_id": str(comment_id),
                },
            )

            return {
                "liked": True,
                "liked_count": count
                }
        
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already liked",
            )