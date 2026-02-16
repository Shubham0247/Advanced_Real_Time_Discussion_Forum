from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select

from backend.services.discussion_service.app.models.comment import Comment
from backend.services.discussion_service.app.repositories.comment_repositories import CommentRepository
from backend.services.discussion_service.app.services.thread_service import ThreadService
from backend.services.discussion_service.app.repositories.like_repository import LikeRepository
from backend.services.auth_service.app.models.user import User
from backend.services.discussion_service.app.core.events import publish_event
from backend.services.discussion_service.app.core.mentions import (
    extract_mentioned_usernames,
    publish_mention_events_for_usernames,
)

class CommentService:
    DELETED_PLACEHOLDER = "This message has been deleted"

    def __init__(self, db: Session):
        self.db = db
        self.repo = CommentRepository(db)
        self.thread_service = ThreadService(db)

    def _attach_author_data_recursive(self, comment: Comment, users_by_id: dict) -> None:
        author_id = getattr(comment, "author_id", None)
        user = users_by_id.get(author_id)
        if user:
            comment.author_username = user.username
            comment.author_name = user.full_name
            comment.author_avatar = user.avatar_url
        for reply in getattr(comment, "replies", []):
            self._attach_author_data_recursive(reply, users_by_id)

    def _attach_author_data_for_tree(self, root_comments: list[Comment]) -> None:
        if not root_comments or not hasattr(self.db, "scalars"):
            return

        author_ids: set[UUID] = set()

        def collect_ids(comment: Comment) -> None:
            if hasattr(comment, "author_id"):
                author_ids.add(comment.author_id)
            for reply in getattr(comment, "replies", []):
                collect_ids(reply)

        for root in root_comments:
            collect_ids(root)

        if not author_ids:
            return
        users = list(self.db.scalars(select(User).where(User.id.in_(author_ids))))
        users_by_id = {user.id: user for user in users}

        for root in root_comments:
            self._attach_author_data_recursive(root, users_by_id)

    def create_comment(self, thread_id: UUID, content: str, author_id: UUID, parent_id: UUID | None):
        
        thread = self.thread_service.get_thread(thread_id)
        parent = None

        if thread.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Thread is locked"
            )

        if parent_id:
            parent = self.repo.get_by_id(parent_id)
            if not parent or parent.thread_id != thread_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid parent comment"
                )

        comment = Comment(
            content=content.strip(),
            thread_id=thread_id,
            author_id=author_id,
            parent_id=parent_id,
        )

        created_comment = self.repo.create(comment)

        created_comment.like_count = 0
        created_comment.is_liked_by_current_user = False
        if hasattr(self.db, "scalar") and hasattr(created_comment, "author_id"):
            user = self.db.scalar(select(User).where(User.id == created_comment.author_id))
            if user:
                created_comment.author_username = user.username
                created_comment.author_name = user.full_name
                created_comment.author_avatar = user.avatar_url

        publish_event(
            channel="thread_updates",
            thread_id=str(thread_id),
            actor_id=str(author_id),
            event="comment.created",
            payload={
                "id": str(created_comment.id),
                "content": created_comment.content,
                "author_id": str(created_comment.author_id),
                "parent_id": str(created_comment.parent_id) if created_comment.parent_id else None,
                "like_count": 0
            }
        )

        # Notify thread owner when someone adds a top-level comment.
        if not parent and thread.author_id != author_id:
            publish_event(
                channel="discussion_events",
                thread_id=str(thread_id),
                actor_id=str(author_id),
                event="thread.commented",
                payload={
                    "owner_id": str(thread.author_id),
                    "comment_id": str(created_comment.id),
                    "preview": created_comment.content[:200],
                },
            )

        if parent and parent.author_id != author_id:
            publish_event(
                channel="discussion_events",
                thread_id=str(thread_id),
                actor_id=str(author_id),
                event="comment.replied",
                payload={
                    "receiver_id": str(parent.author_id),
                    "comment_id": str(created_comment.id),
                    "parent_id": str(parent.id),
                    "preview": created_comment.content[:200],
                },
            )

        publish_mention_events_for_usernames(
            self.db,
            usernames=extract_mentioned_usernames(created_comment.content),
            actor_id=author_id,
            thread_id=thread_id,
            source_type="comment",
            source_id=created_comment.id,
            preview=created_comment.content,
        )


        return created_comment
    
    def _attach_like_data_recursive(self, comment, like_repo, current_user):
        comment.like_count = like_repo.count_comment_likes(comment.id)
        comment.is_liked_by_current_user = like_repo.is_comment_liked_by_user(
            comment.id,
            current_user.id
        )

        for reply in comment.replies:
            self._attach_like_data_recursive(reply, like_repo, current_user)


    def get_thread_comments(self, thread_id: UUID, current_user):
        comments = self.repo.get_thread_comments(thread_id)
        like_repo = LikeRepository(self.db)

        for comment in comments:
            comment.replies = []

        
        comment_map = {comment.id: comment for comment in comments}
        tree = []

        for comment in comments:
            if comment.parent_id:
                parent = comment_map.get(comment.parent_id)
                if parent:
                    parent.replies.append(comment)
            else:
                tree.append(comment)

        
        for root_comment in tree:
            self._attach_like_data_recursive(root_comment, like_repo, current_user)
        self._attach_author_data_for_tree(tree)

        return tree

    def search_comments(self, keyword: str, page: int, size: int, current_user):
        skip = (page - 1) * size
        comments = self.repo.search_comments(keyword, skip, size)
        total = self.repo.count_search_comments(keyword)
        like_repo = LikeRepository(self.db)

        for comment in comments:
            comment.replies = []
            comment.like_count = like_repo.count_comment_likes(comment.id)
            comment.is_liked_by_current_user = like_repo.is_comment_liked_by_user(
                comment.id,
                current_user.id,
            ) if current_user else False
        self._attach_author_data_for_tree(comments)

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": comments,
        }

    def list_comments(self, page: int, size: int, current_user):
        skip = (page - 1) * size
        comments = self.repo.list_comments(skip, size)
        total = self.repo.count_comments()
        like_repo = LikeRepository(self.db)

        for comment in comments:
            comment.replies = []
            comment.like_count = like_repo.count_comment_likes(comment.id)
            comment.is_liked_by_current_user = like_repo.is_comment_liked_by_user(
                comment.id,
                current_user.id,
            ) if current_user else False
        self._attach_author_data_for_tree(comments)

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": comments,
        }


    def update_comment(self, comment_id: UUID, content: str, current_user):
        comment = self.repo.get_by_id(comment_id)

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        user_roles = {role.name for role in getattr(current_user, "roles", [])}
        if comment.author_id != current_user.id and not (
            "moderator" in user_roles or "admin" in user_roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this comment",
            )

        previous_mentions = extract_mentioned_usernames(comment.content)
        comment.content = content.strip()
        updated_comment = self.repo.update(comment)
        updated_comment.like_count = 0
        updated_comment.is_liked_by_current_user = False
        if hasattr(self.db, "scalar"):
            like_repo = LikeRepository(self.db)
            updated_comment.like_count = like_repo.count_comment_likes(updated_comment.id)
            updated_comment.is_liked_by_current_user = like_repo.is_comment_liked_by_user(
                updated_comment.id,
                current_user.id,
            )
        if getattr(updated_comment, "replies", None) is None:
            updated_comment.replies = []

        publish_event(
            channel="thread_updates",
            thread_id=str(comment.thread_id),
            actor_id=str(current_user.id),
            event="comment.updated",
            payload={
                "id": str(comment.id),
                "content": comment.content
            }
        )

        updated_mentions = extract_mentioned_usernames(updated_comment.content)
        newly_added_mentions = updated_mentions - previous_mentions

        publish_mention_events_for_usernames(
            self.db,
            usernames=newly_added_mentions,
            actor_id=current_user.id,
            thread_id=comment.thread_id,
            source_type="comment",
            source_id=comment.id,
            preview=updated_comment.content,
        )
        if hasattr(self.db, "scalar") and hasattr(updated_comment, "author_id"):
            user = self.db.scalar(select(User).where(User.id == updated_comment.author_id))
            if user:
                updated_comment.author_username = user.username
                updated_comment.author_name = user.full_name
                updated_comment.author_avatar = user.avatar_url

        return updated_comment

    def delete_comment(self, comment_id: UUID, current_user):
        comment = self.repo.get_by_id(comment_id)

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        user_roles = {role.name for role in getattr(current_user, "roles", [])}
        is_thread_owner = False
        if hasattr(self.db, "scalar"):
            thread = self.thread_service.get_thread(comment.thread_id, current_user)
            is_thread_owner = thread.author_id == current_user.id
        if comment.author_id != current_user.id and not is_thread_owner and not (
            "moderator" in user_roles or "admin" in user_roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this comment",
            )

        def has_children(target_comment):
            if hasattr(self.repo, "has_children"):
                return self.repo.has_children(target_comment.id)
            return bool(getattr(target_comment, "replies", []))

        # If comment has replies, keep it in tree but anonymize content.
        if has_children(comment):
            comment.is_deleted = True
            comment.content = self.DELETED_PLACEHOLDER
            deleted_comment = self.repo.update(comment)
        else:
            # Leaf comments should disappear from UI.
            if hasattr(self.repo, "hard_delete"):
                parent_id = comment.parent_id
                self.repo.hard_delete(comment)
                deleted_comment = comment

                # Cleanup chain: if parent is already soft-deleted and now has no children,
                # remove it as well so only meaningful placeholders remain.
                while parent_id:
                    parent = self.repo.get_by_id(parent_id)
                    if not parent:
                        break
                    next_parent_id = parent.parent_id
                    if parent.is_deleted and not has_children(parent):
                        self.repo.hard_delete(parent)
                    else:
                        break
                    parent_id = next_parent_id
            else:
                # Backward compatibility for tests/mocks that do not implement hard_delete.
                deleted_comment = self.repo.soft_delete(comment)

        publish_event(
            channel="thread_updates",
            thread_id=str(comment.thread_id),
            actor_id=str(current_user.id),
            event="comment.deleted",
            payload={
                "id": str(comment.id)
            }
        )

        return deleted_comment
