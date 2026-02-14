import os
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")

from backend.services.notification_service.app.api import notifications as notifications_api  # noqa: E402
from backend.services.notification_service.app.services.notification_service import NotificationService  # noqa: E402


def test_notifications_api_routes_delegate_to_service(monkeypatch):
    class FakeService:
        def __init__(self, _db):
            pass

        def list_my_notifications(self, _uid, _page, _size):
            return {"total": 1, "page": 1, "size": 20, "items": []}

        def unread_count(self, _uid):
            return 3

        def mark_one_read(self, _nid, _uid):
            return SimpleNamespace(
                id=uuid4(),
                user_id=_uid,
                actor_id=uuid4(),
                type="mention",
                reference_id=uuid4(),
                message="m",
                is_read=True,
                created_at="2024-01-01T00:00:00Z",
            )

        def mark_all_read(self, _uid):
            return 5

    monkeypatch.setattr(notifications_api, "NotificationService", FakeService)
    user = SimpleNamespace(id=uuid4())

    out_list = notifications_api.list_my_notifications(db=object(), current_user=user)
    out_count = notifications_api.unread_count(db=object(), current_user=user)
    out_mark_all = notifications_api.mark_all_read(db=object(), current_user=user)

    assert out_list["total"] == 1
    assert out_count["unread_count"] == 3
    assert out_mark_all["updated_count"] == 5


def test_notification_service_mark_one_read_not_found(monkeypatch):
    service = NotificationService(db=object())

    class FakeRepo:
        def get_user_notification_by_id(self, _nid, _uid):
            return None

    service.repo = FakeRepo()

    with pytest.raises(HTTPException) as e:
        service.mark_one_read(uuid4(), uuid4())
    assert e.value.status_code == 404


def test_notification_service_list_and_mark_all(monkeypatch):
    service = NotificationService(db=object())

    class FakeRepo:
        def list_user_notifications(self, _uid, *, skip, limit):
            assert skip == 20
            assert limit == 20
            return [SimpleNamespace()]

        def count_user_notifications(self, _uid):
            return 21

        def count_unread_notifications(self, _uid):
            return 4

        def mark_all_as_read(self, _uid):
            return 4

    service.repo = FakeRepo()

    out = service.list_my_notifications(uuid4(), page=2, size=20)
    unread = service.unread_count(uuid4())
    updated = service.mark_all_read(uuid4())

    assert out["total"] == 21
    assert out["page"] == 2
    assert len(out["items"]) == 1
    assert unread == 4
    assert updated == 4
