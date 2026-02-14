import asyncio
import os
import json
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")

from backend.services.notification_service.app.core import redis_listener  # noqa: E402


def test_handle_mention_creates_notification_and_publishes(monkeypatch):
    user_id = uuid4()
    actor_id = uuid4()
    thread_id = uuid4()
    source_id = uuid4()

    event = {
        "event": "mention",
        "thread_id": str(thread_id),
        "actor_id": str(actor_id),
        "payload": {
            "mentioned_user_id": str(user_id),
            "source_id": str(source_id),
            "source_type": "comment",
            "preview": "you were mentioned",
        },
    }

    created = []
    published = []

    class FakeDB:
        def close(self):
            return None

    class FakeRepo:
        def __init__(self, _db):
            pass

        def create(self, notification):
            notification.id = uuid4()
            created.append(notification)
            return notification

    class FakeRedis:
        async def publish(self, channel, message):
            published.append((channel, message))

    monkeypatch.setattr(redis_listener, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(redis_listener, "NotificationRepository", FakeRepo)
    monkeypatch.setattr(redis_listener, "redis_client", FakeRedis())

    asyncio.run(redis_listener.handle_event(event))

    assert len(created) == 1
    assert created[0].type == "mention"
    assert len(published) == 1
    assert published[0][0] == "user_notifications"


def test_handle_mention_missing_fields_returns_without_publishing(monkeypatch):
    event = {
        "event": "mention",
        "thread_id": str(uuid4()),
        "actor_id": str(uuid4()),
        "payload": {
            "mentioned_user_id": str(uuid4()),
            # source_id intentionally missing
        },
    }

    created = []
    published = []

    class FakeDB:
        def close(self):
            return None

    class FakeRepo:
        def __init__(self, _db):
            pass

        def create(self, notification):
            created.append(notification)
            return notification

    class FakeRedis:
        async def publish(self, channel, message):
            published.append((channel, message))

    monkeypatch.setattr(redis_listener, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(redis_listener, "NotificationRepository", FakeRepo)
    monkeypatch.setattr(redis_listener, "redis_client", FakeRedis())

    asyncio.run(redis_listener.handle_event(event))

    assert created == []
    assert published == []


def test_handle_thread_liked_creates_notification_and_publishes(monkeypatch):
    owner_id = uuid4()
    actor_id = uuid4()
    thread_id = uuid4()

    event = {
        "event": "thread.liked",
        "thread_id": str(thread_id),
        "actor_id": str(actor_id),
        "payload": {"owner_id": str(owner_id)},
    }

    created = []
    published = []

    class FakeDB:
        def close(self):
            return None

    class FakeRepo:
        def __init__(self, _db):
            pass

        def create(self, notification):
            notification.id = uuid4()
            created.append(notification)
            return notification

    class FakeRedis:
        async def publish(self, channel, message):
            published.append((channel, json.loads(message)))

    monkeypatch.setattr(redis_listener, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(redis_listener, "NotificationRepository", FakeRepo)
    monkeypatch.setattr(redis_listener, "redis_client", FakeRedis())

    asyncio.run(redis_listener.handle_event(event))

    assert len(created) == 1
    assert created[0].type == "thread.liked"
    assert len(published) == 1
    assert published[0][0] == "user_notifications"
    assert published[0][1]["event"] == "thread.liked"


def test_handle_comment_replied_creates_notification_and_publishes(monkeypatch):
    receiver_id = uuid4()
    actor_id = uuid4()
    thread_id = uuid4()
    comment_id = uuid4()

    event = {
        "event": "comment.replied",
        "thread_id": str(thread_id),
        "actor_id": str(actor_id),
        "payload": {
            "receiver_id": str(receiver_id),
            "comment_id": str(comment_id),
            "preview": "reply text",
        },
    }

    created = []
    published = []

    class FakeDB:
        def close(self):
            return None

    class FakeRepo:
        def __init__(self, _db):
            pass

        def create(self, notification):
            notification.id = uuid4()
            created.append(notification)
            return notification

    class FakeRedis:
        async def publish(self, channel, message):
            published.append((channel, json.loads(message)))

    monkeypatch.setattr(redis_listener, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(redis_listener, "NotificationRepository", FakeRepo)
    monkeypatch.setattr(redis_listener, "redis_client", FakeRedis())

    asyncio.run(redis_listener.handle_event(event))

    assert len(created) == 1
    assert created[0].type == "comment.replied"
    assert len(published) == 1
    assert published[0][0] == "user_notifications"
    assert published[0][1]["event"] == "comment.replied"


def test_handle_comment_replied_missing_fields_returns_without_publishing(monkeypatch):
    event = {
        "event": "comment.replied",
        "thread_id": str(uuid4()),
        "actor_id": str(uuid4()),
        "payload": {"receiver_id": str(uuid4())},  # missing comment_id
    }

    created = []
    published = []

    class FakeDB:
        def close(self):
            return None

    class FakeRepo:
        def __init__(self, _db):
            pass

        def create(self, notification):
            created.append(notification)
            return notification

    class FakeRedis:
        async def publish(self, channel, message):
            published.append((channel, message))

    monkeypatch.setattr(redis_listener, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(redis_listener, "NotificationRepository", FakeRepo)
    monkeypatch.setattr(redis_listener, "redis_client", FakeRedis())

    asyncio.run(redis_listener.handle_event(event))

    assert created == []
    assert published == []


def test_start_notification_listener_consumes_messages(monkeypatch):
    handled = []

    class FakePubSub:
        async def subscribe(self, _channel):
            return None

        async def listen(self):
            yield {"type": "subscribe", "data": 1}
            yield {"type": "message", "data": "{\"event\":\"mention\"}"}
            yield {"type": "message", "data": "invalid-json"}

    class FakeRedis:
        def pubsub(self):
            return FakePubSub()

    async def fake_handle_event(event):
        handled.append(event)
        raise RuntimeError("stop-loop")

    monkeypatch.setattr(redis_listener, "redis_client", FakeRedis())
    monkeypatch.setattr(redis_listener, "handle_event", fake_handle_event)

    asyncio.run(redis_listener.start_notification_listener())

    assert len(handled) == 1
    assert handled[0]["event"] == "mention"
