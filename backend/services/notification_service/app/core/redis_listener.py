import redis.asyncio as redis
import json
from uuid import UUID
from sqlalchemy import select

from backend.services.notification_service.app.repositories.notification_repositories import NotificationRepository
from backend.services.notification_service.app.models.notification import Notification
from backend.services.auth_service.app.models.user import User
from backend.shared.database.session import SessionLocal

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


async def start_notification_listener():
    print("Notification service listening...")

    pubsub = redis_client.pubsub()
    await pubsub.subscribe("discussion_events")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        try:
            data = json.loads(message["data"])
            await handle_event(data)
        except json.JSONDecodeError:
            print("Invalid JSON in discussion_events payload")
        except Exception as e:
            print(f"Notification listener error: {e}")


async def handle_event(event: dict):
    event_type = event.get("event")
    thread_id = event.get("thread_id")
    actor_id = event.get("actor_id")
    payload = event.get("payload", {})

    if not event_type:
        return

    db = SessionLocal()
    repo = NotificationRepository(db)

    try:
        actor_user = db.scalar(select(User).where(User.id == UUID(actor_id))) if actor_id else None
        actor_name = actor_user.username if actor_user else "Someone"

        if event_type == "thread.liked":
            owner_id = payload.get("owner_id")
            if not (owner_id and thread_id and actor_id):
                return

            receiver_id = UUID(owner_id)
            actor_uuid = UUID(actor_id)
            thread_uuid = UUID(thread_id)
            if receiver_id == actor_uuid:
                return

            notification = Notification(
                user_id=receiver_id,
                actor_id=actor_uuid,
                type="thread.liked",
                reference_id=thread_uuid,
                message=f"{actor_name} liked your thread",
            )

            repo.create(notification)

            await redis_client.publish(
                "user_notifications",
                json.dumps(
                    {
                        "type": "notification",
                        "user_id": str(receiver_id),
                        "message": notification.message,
                        "notification_id": str(notification.id),
                        "event": event_type,
                        "thread_id": str(thread_uuid),
                        "actor_id": str(actor_uuid),
                        "reference_id": str(thread_uuid),
                    }
                ),
            )

        elif event_type == "comment.liked":
            owner_id = payload.get("owner_id")
            comment_id = payload.get("comment_id")
            if not (owner_id and thread_id and comment_id and actor_id):
                return

            receiver_id = UUID(owner_id)
            actor_uuid = UUID(actor_id)
            thread_uuid = UUID(thread_id)
            if receiver_id == actor_uuid:
                return

            notification = Notification(
                user_id=receiver_id,
                actor_id=actor_uuid,
                type="comment.liked",
                reference_id=thread_uuid,
                message=f"{actor_name} liked your comment",
            )

            repo.create(notification)

            await redis_client.publish(
                "user_notifications",
                json.dumps(
                    {
                        "type": "notification",
                        "user_id": str(receiver_id),
                        "message": notification.message,
                        "notification_id": str(notification.id),
                        "event": event_type,
                        "thread_id": str(thread_uuid),
                        "comment_id": str(comment_id),
                        "actor_id": str(actor_uuid),
                        "reference_id": str(thread_uuid),
                    }
                ),
            )

        elif event_type == "mention":
            mentioned_user_id = payload.get("mentioned_user_id")
            source_id = payload.get("source_id")
            source_type = payload.get("source_type", "content")
            preview = payload.get("preview", "")
            if not (mentioned_user_id and source_id and actor_id):
                return

            receiver_id = UUID(mentioned_user_id)
            actor_uuid = UUID(actor_id)
            source_uuid = UUID(source_id)
            if receiver_id == actor_uuid:
                return
            reference_uuid = UUID(thread_id) if thread_id else source_uuid
            mention_type = f"mention.{source_type}" if source_type in {"thread", "comment"} else "mention"

            notification = Notification(
                user_id=receiver_id,
                actor_id=actor_uuid,
                type=mention_type,
                reference_id=reference_uuid,
                message=f"{actor_name} mentioned you in a {source_type}",
            )

            repo.create(notification)

            await redis_client.publish(
                "user_notifications",
                json.dumps(
                    {
                        "type": "notification",
                        "user_id": str(receiver_id),
                        "message": notification.message,
                        "notification_id": str(notification.id),
                        "event": event_type,
                        "thread_id": thread_id,
                        "actor_id": str(actor_uuid),
                        "source_id": str(source_uuid),
                        "source_type": source_type,
                        "reference_id": str(reference_uuid),
                        "preview": preview,
                    }
                ),
            )

        elif event_type == "comment.replied":
            receiver_id = payload.get("receiver_id")
            comment_id = payload.get("comment_id")
            preview = payload.get("preview", "")
            if not (receiver_id and comment_id and actor_id):
                return

            receiver_uuid = UUID(receiver_id)
            actor_uuid = UUID(actor_id)
            comment_uuid = UUID(comment_id)
            if receiver_uuid == actor_uuid:
                return
            thread_uuid = UUID(thread_id) if thread_id else comment_uuid

            notification = Notification(
                user_id=receiver_uuid,
                actor_id=actor_uuid,
                type="comment.replied",
                reference_id=thread_uuid,
                message=f"{actor_name} replied to your comment",
            )

            repo.create(notification)

            await redis_client.publish(
                "user_notifications",
                json.dumps(
                    {
                        "type": "notification",
                        "user_id": str(receiver_uuid),
                        "message": notification.message,
                        "notification_id": str(notification.id),
                        "event": event_type,
                        "thread_id": str(thread_uuid),
                        "actor_id": str(actor_uuid),
                        "comment_id": str(comment_uuid),
                        "reference_id": str(thread_uuid),
                        "preview": preview,
                    }
                ),
            )

        elif event_type == "thread.commented":
            owner_id = payload.get("owner_id")
            comment_id = payload.get("comment_id")
            preview = payload.get("preview", "")
            if not (owner_id and thread_id and actor_id):
                return

            receiver_uuid = UUID(owner_id)
            actor_uuid = UUID(actor_id)
            thread_uuid = UUID(thread_id)
            if receiver_uuid == actor_uuid:
                return

            notification = Notification(
                user_id=receiver_uuid,
                actor_id=actor_uuid,
                type="thread.commented",
                reference_id=thread_uuid,
                message=f"{actor_name} commented on your thread",
            )
            repo.create(notification)

            await redis_client.publish(
                "user_notifications",
                json.dumps(
                    {
                        "type": "notification",
                        "user_id": str(receiver_uuid),
                        "message": notification.message,
                        "notification_id": str(notification.id),
                        "event": event_type,
                        "thread_id": str(thread_uuid),
                        "actor_id": str(actor_uuid),
                        "comment_id": str(comment_id) if comment_id else None,
                        "reference_id": str(thread_uuid),
                        "preview": preview,
                    }
                ),
            )

    finally:
        db.close()
