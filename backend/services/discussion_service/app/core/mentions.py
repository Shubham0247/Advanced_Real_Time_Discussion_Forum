import re
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.services.auth_service.app.models.user import User
from backend.services.discussion_service.app.core.events import publish_event

MENTION_PATTERN = re.compile(r"(?<!\w)@([A-Za-z0-9_]{3,50})")


def extract_mentioned_usernames(text: str) -> set[str]:
    if not text:
        return set()
    return {match.group(1) for match in MENTION_PATTERN.finditer(text)}


def publish_mention_events_for_usernames(
    db: Session,
    *,
    usernames: set[str],
    actor_id: UUID,
    thread_id: UUID,
    source_type: str,
    source_id: UUID,
    preview: str,
) -> None:
    if not usernames:
        return

    lowered = {username.lower() for username in usernames}
    users = list(
        db.scalars(
            select(User).where(func.lower(User.username).in_(lowered))
        )
    )

    for user in users:
        if user.id == actor_id:
            continue

        publish_event(
            channel="discussion_events",
            event="mention",
            thread_id=str(thread_id),
            actor_id=str(actor_id),
            payload={
                "mentioned_user_id": str(user.id),
                "mentioned_username": user.username,
                "source_type": source_type,
                "source_id": str(source_id),
                "preview": preview[:200],
            },
        )
