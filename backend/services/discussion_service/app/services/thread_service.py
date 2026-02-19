from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func

from backend.services.discussion_service.app.models.thread import Thread
from backend.services.discussion_service.app.models.comment import Comment
from backend.services.discussion_service.app.repositories.thread_repositories import ThreadRepository
from backend.services.discussion_service.app.repositories.like_repository import LikeRepository
from backend.services.discussion_service.app.core.events import publish_event
from backend.services.auth_service.app.models.user import User
from backend.services.discussion_service.app.core.mentions import (
    extract_mentioned_usernames,
    publish_mention_events_for_usernames,
)


class ThreadService:
    """
    Handles business logic related to threads.
    """

    def __init__(self, db: Session):
        """Initialize the thread service with a database session and repository."""
        self.db = db
        self.thread_repo = ThreadRepository(db)

    def _attach_author_data(self, thread: Thread) -> None:
        """Populate author metadata on a single thread object when available."""
        if not hasattr(self.db, "scalar") or not hasattr(thread, "author_id"):
            return
        user = self.db.scalar(select(User).where(User.id == thread.author_id))
        if user:
            thread.author_username = user.username
            thread.author_name = user.full_name
            thread.author_avatar = user.avatar_url

    def _attach_author_data_for_threads(self, threads: list[Thread]) -> None:
        """Populate author metadata for a list of thread objects."""
        if not threads or not hasattr(self.db, "scalars"):
            return
        author_ids = {thread.author_id for thread in threads if hasattr(thread, "author_id")}
        if not author_ids:
            return
        users = list(self.db.scalars(select(User).where(User.id.in_(author_ids))))
        users_by_id = {user.id: user for user in users}
        for thread in threads:
            author_id = getattr(thread, "author_id", None)
            user = users_by_id.get(author_id)
            if user:
                thread.author_username = user.username
                thread.author_name = user.full_name
                thread.author_avatar = user.avatar_url

    def _attach_comment_count(self, thread: Thread) -> None:
        """Attach the non-deleted comment count to a single thread."""
        if not hasattr(self.db, "scalar") or not hasattr(thread, "id"):
            return
        thread.comment_count = (
            self.db.scalar(
                select(func.count()).where(
                    Comment.thread_id == thread.id,
                    Comment.is_deleted == False,
                )
            )
            or 0
        )

    def _attach_comment_counts_for_threads(self, threads: list[Thread]) -> None:
        """Attach non-deleted comment counts for each thread in a list."""
        if not threads or not hasattr(self.db, "execute"):
            return
        thread_ids = [thread.id for thread in threads if hasattr(thread, "id")]
        if not thread_ids:
            return

        rows = list(
            self.db.execute(
                select(Comment.thread_id, func.count(Comment.id))
                .where(
                    Comment.thread_id.in_(thread_ids),
                    Comment.is_deleted == False,
                )
                .group_by(Comment.thread_id)
            ).all()
        )
        count_map = {thread_id: count for thread_id, count in rows}
        for thread in threads:
            thread.comment_count = int(count_map.get(thread.id, 0))


    def create_thread(
        self,
        title: str,
        description: str,
        author_id: UUID,
        image_url: str | None = None,
    ) -> Thread:
        """Create a thread, publish events, and return enriched thread data."""
        thread = Thread(
            title=title.strip(),
            description=description.strip(),
            image_url=image_url,
            author_id=author_id,
        )

        created_thread = self.thread_repo.create(thread)

        created_thread.like_count = 0
        created_thread.comment_count = 0
        created_thread.is_liked_by_current_user = False
        self._attach_author_data(created_thread)

        publish_event(
            channel="thread_updates",
            thread_id=str(created_thread.id),
            actor_id=str(author_id),
            event="thread.created",
            payload={
                "id": str(created_thread.id),
                "title": created_thread.title,
                "image_url": created_thread.image_url,
            },
        )

        thread_text = f"{created_thread.title}\n{created_thread.description}"
        publish_mention_events_for_usernames(
            self.db,
            usernames=extract_mentioned_usernames(thread_text),
            actor_id=author_id,
            thread_id=created_thread.id,
            source_type="thread",
            source_id=created_thread.id,
            preview=thread_text,
        )

        return created_thread


    def get_thread(self, thread_id: UUID, current_user=None) -> Thread:
        """Retrieve a thread by id and enrich it with like/comment metadata."""

        thread = self.thread_repo.get_by_id(thread_id)
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found",
            )

        like_repo = LikeRepository(self.db)

        thread.like_count = like_repo.count_thread_likes(thread_id)
        self._attach_comment_count(thread)
        thread.is_liked_by_current_user = (
            like_repo.is_thread_liked_by_user(thread_id, current_user.id)
            if current_user
            else False
        )
        self._attach_author_data(thread)

        return thread


    def list_threads(
        self,
        page: int,
        size: int,
        current_user,
        moderation_status: str | None = None,
    ):
        """Return a paginated list of threads with engagement and author data."""
        skip = (page - 1) * size
        if moderation_status is None:
            threads = self.thread_repo.list_threads(skip, size)
            total = self.thread_repo.count_threads()
        else:
            threads = self.thread_repo.list_threads(skip, size, moderation_status=moderation_status)
            total = self.thread_repo.count_threads(moderation_status=moderation_status)

        like_repo = LikeRepository(self.db)

        for thread in threads:
            thread.like_count = like_repo.count_thread_likes(thread.id)
            thread.is_liked_by_current_user = (
                like_repo.is_thread_liked_by_user(thread.id, current_user.id)
                if current_user
                else False
            )
        self._attach_comment_counts_for_threads(threads)
        self._attach_author_data_for_threads(threads)

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": threads,
        }

    def search_threads(
        self,
        keyword: str,
        page: int,
        size: int,
        current_user,
        moderation_status: str | None = None,
    ):
        """Search threads by keyword and return paginated enriched results."""
        skip = (page - 1) * size
        if moderation_status is None:
            threads = self.thread_repo.search_threads(keyword, skip, size)
            total = self.thread_repo.count_search_threads(keyword)
        else:
            threads = self.thread_repo.search_threads(
                keyword,
                skip,
                size,
                moderation_status=moderation_status,
            )
            total = self.thread_repo.count_search_threads(keyword, moderation_status=moderation_status)

        like_repo = LikeRepository(self.db)

        for thread in threads:
            thread.like_count = like_repo.count_thread_likes(thread.id)
            thread.is_liked_by_current_user = (
                like_repo.is_thread_liked_by_user(thread.id, current_user.id)
                if current_user
                else False
            )
        self._attach_comment_counts_for_threads(threads)
        self._attach_author_data_for_threads(threads)

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": threads,
        }

    def update_moderation_status(self, thread_id: UUID, moderation_status: str):
        """Validate and update moderation status for a thread."""
        allowed = {"pending", "reported", "approved"}
        moderation_status = moderation_status.strip().lower()
        if moderation_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid moderation status",
            )

        thread = self.thread_repo.get_by_id(thread_id)
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found",
            )

        thread.moderation_status = moderation_status
        return self.thread_repo.update(thread)

    def list_my_threads(self, page: int, size: int, current_user):
        """List paginated threads created by the current user."""
        skip = (page - 1) * size
        threads = self.thread_repo.list_threads_by_author(current_user.id, skip, size)
        total = self.thread_repo.count_threads_by_author(current_user.id)

        like_repo = LikeRepository(self.db)
        for thread in threads:
            thread.like_count = like_repo.count_thread_likes(thread.id)
            thread.is_liked_by_current_user = like_repo.is_thread_liked_by_user(
                thread.id,
                current_user.id,
            )
        self._attach_comment_counts_for_threads(threads)
        self._attach_author_data_for_threads(threads)

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": threads,
        }


    def update_thread(self, thread_id: UUID, data: dict, current_user):
        """Update a thread after permission checks and emit update events."""

        thread = self.thread_repo.get_by_id(thread_id)
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found",
            )

        user_roles = {role.name for role in current_user.roles}

        if thread.author_id != current_user.id and not (
            "moderator" in user_roles or "admin" in user_roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this thread",
            )

        old_thread_text = f"{thread.title}\n{thread.description}"

        if "title" in data:
            thread.title = data["title"].strip()

        if "description" in data:
            thread.description = data["description"].strip()

        if "image_url" in data:
            thread.image_url = data["image_url"]

        if "is_locked" in data:
            if "moderator" not in user_roles and "admin" not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only moderators/admin can lock/unlock threads",
                )
            thread.is_locked = data["is_locked"]

        updated_thread = self.thread_repo.update(thread)

        
        like_repo = LikeRepository(self.db)
        updated_thread.like_count = like_repo.count_thread_likes(thread.id)
        self._attach_comment_count(updated_thread)
        updated_thread.is_liked_by_current_user = like_repo.is_thread_liked_by_user(
            thread.id,
            current_user.id,
        )
        self._attach_author_data(updated_thread)

        publish_event(
            channel="thread_updates",
            thread_id=str(thread.id),
            actor_id=str(current_user.id),
            event="thread.updated",
            payload={
                "id": str(thread.id),
                "title": thread.title,
                "description": thread.description,
                "image_url": thread.image_url,
                "is_locked": thread.is_locked,
            },
        )

        new_thread_text = f"{thread.title}\n{thread.description}"
        old_mentions = extract_mentioned_usernames(old_thread_text)
        new_mentions = extract_mentioned_usernames(new_thread_text)
        newly_added_mentions = new_mentions - old_mentions

        publish_mention_events_for_usernames(
            self.db,
            usernames=newly_added_mentions,
            actor_id=current_user.id,
            thread_id=thread.id,
            source_type="thread",
            source_id=thread.id,
            preview=new_thread_text,
        )

        return updated_thread


    def delete_thread(self, thread_id: UUID, current_user):
        """Soft delete a thread after authorization checks and publish an event."""

        thread = self.thread_repo.get_by_id(thread_id)
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found",
            )

        user_roles = {role.name for role in current_user.roles}

        if thread.author_id != current_user.id and not (
            "moderator" in user_roles or "admin" in user_roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this thread",
            )

        deleted_thread = self.thread_repo.soft_delete(thread)

        publish_event(
            channel="thread_updates",
            thread_id=str(thread.id),
            actor_id=str(current_user.id),
            event="thread.deleted",
            payload={"id": str(thread.id)},
        )

        return deleted_thread
