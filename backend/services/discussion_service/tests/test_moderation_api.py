from types import SimpleNamespace
from uuid import uuid4

from backend.services.discussion_service.app.api import moderation as moderation_api


def test_moderation_threads_uses_list_or_search(monkeypatch):
    class FakeThreadService:
        def __init__(self, _db):
            pass

        def list_threads(self, page, size, current_user):
            return {"total": 1, "page": page, "size": size, "items": []}

        def search_threads(self, q, page, size, current_user):
            assert q == "python"
            return {"total": 2, "page": page, "size": size, "items": []}

    monkeypatch.setattr(moderation_api, "ThreadService", FakeThreadService)
    current_user = SimpleNamespace(id=uuid4(), roles=[SimpleNamespace(name="moderator")])

    out_list = moderation_api.moderation_threads(
        q=None,
        page=1,
        size=20,
        db=object(),
        current_user=current_user,
    )
    out_search = moderation_api.moderation_threads(
        q="python",
        page=1,
        size=20,
        db=object(),
        current_user=current_user,
    )

    assert out_list["total"] == 1
    assert out_search["total"] == 2


def test_moderation_comments_uses_list_or_search(monkeypatch):
    class FakeCommentService:
        def __init__(self, _db):
            pass

        def list_comments(self, page, size, current_user):
            return {"total": 3, "page": page, "size": size, "items": []}

        def search_comments(self, q, page, size, current_user):
            assert q == "mention"
            return {"total": 1, "page": page, "size": size, "items": []}

    monkeypatch.setattr(moderation_api, "CommentService", FakeCommentService)
    current_user = SimpleNamespace(id=uuid4(), roles=[SimpleNamespace(name="admin")])

    out_list = moderation_api.moderation_comments(
        q=None,
        page=1,
        size=20,
        db=object(),
        current_user=current_user,
    )
    out_search = moderation_api.moderation_comments(
        q="mention",
        page=1,
        size=20,
        db=object(),
        current_user=current_user,
    )

    assert out_list["total"] == 3
    assert out_search["total"] == 1
