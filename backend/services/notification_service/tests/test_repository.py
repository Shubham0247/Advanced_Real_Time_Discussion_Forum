from datetime import datetime, timezone
from uuid import uuid4

from backend.services.notification_service.app.models.notification import Notification
from backend.services.notification_service.app.repositories.notification_repositories import NotificationRepository


def test_repository_create_calls_db_methods():
    calls = {"add": 0, "commit": 0, "refresh": 0}

    class FakeDB:
        def add(self, _obj):
            calls["add"] += 1

        def commit(self):
            calls["commit"] += 1

        def refresh(self, _obj):
            calls["refresh"] += 1

    repo = NotificationRepository(FakeDB())
    n = Notification(
        user_id=uuid4(),
        actor_id=uuid4(),
        type="mention",
        reference_id=uuid4(),
        message="m",
        created_at=datetime.now(timezone.utc),
    )

    out = repo.create(n)
    assert out is n
    assert calls == {"add": 1, "commit": 1, "refresh": 1}


def test_repository_get_user_notifications_returns_scalars():
    rows = [object(), object()]

    class FakeScalars:
        def __iter__(self):
            return iter(rows)

    class FakeDB:
        def scalars(self, _query):
            return FakeScalars()

    repo = NotificationRepository(FakeDB())
    out = repo.get_user_notifications(uuid4())
    assert out == rows
