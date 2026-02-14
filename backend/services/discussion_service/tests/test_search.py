from types import SimpleNamespace
from uuid import uuid4

from backend.services.discussion_service.app.api import comments as comments_api
from backend.services.discussion_service.app.api import threads as threads_api
from backend.services.discussion_service.app.services.comment_service import CommentService
from backend.services.discussion_service.app.services.thread_service import ThreadService


def test_threads_search_api_calls_service(monkeypatch):
    expected = {"total": 1, "page": 1, "size": 10, "items": []}

    class FakeThreadService:
        def __init__(self, _db):
            pass

        def search_threads(self, q, page, size, current_user):
            assert q == "python"
            assert page == 1
            assert size == 10
            assert current_user.id
            return expected

    monkeypatch.setattr(threads_api, "ThreadService", FakeThreadService)
    out = threads_api.search_threads(
        q="python",
        page=1,
        size=10,
        db=object(),
        current_user=SimpleNamespace(id=uuid4()),
    )
    assert out == expected


def test_comments_search_api_calls_service(monkeypatch):
    expected = {"total": 2, "page": 1, "size": 10, "items": []}

    class FakeCommentService:
        def __init__(self, _db):
            pass

        def search_comments(self, q, page, size, current_user):
            assert q == "mention"
            assert page == 1
            assert size == 10
            assert current_user.id
            return expected

    monkeypatch.setattr(comments_api, "CommentService", FakeCommentService)
    out = comments_api.search_comments(
        q="mention",
        page=1,
        size=10,
        db=object(),
        current_user=SimpleNamespace(id=uuid4()),
    )
    assert out == expected


def test_thread_and_comment_search_service_attach_like_metadata(monkeypatch):
    user = SimpleNamespace(id=uuid4())
    thread_obj = SimpleNamespace(id=uuid4())
    comment_obj = SimpleNamespace(id=uuid4(), replies=[])

    class FakeThreadRepo:
        def search_threads(self, keyword, skip, limit):
            assert keyword == "fastapi"
            assert skip == 0
            assert limit == 10
            return [thread_obj]

        def count_search_threads(self, keyword):
            assert keyword == "fastapi"
            return 1

    class FakeCommentRepo:
        def search_comments(self, keyword, skip, limit):
            assert keyword == "fastapi"
            assert skip == 0
            assert limit == 10
            return [comment_obj]

        def count_search_comments(self, keyword):
            assert keyword == "fastapi"
            return 1

    class FakeLikeRepo:
        def __init__(self, _db):
            pass

        def count_thread_likes(self, _thread_id):
            return 5

        def is_thread_liked_by_user(self, _thread_id, _user_id):
            return True

        def count_comment_likes(self, _comment_id):
            return 3

        def is_comment_liked_by_user(self, _comment_id, _user_id):
            return False

    thread_service = ThreadService(SimpleNamespace())
    thread_service.thread_repo = FakeThreadRepo()

    comment_service = CommentService(SimpleNamespace())
    comment_service.repo = FakeCommentRepo()

    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.thread_service.LikeRepository",
        FakeLikeRepo,
    )
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.LikeRepository",
        FakeLikeRepo,
    )

    thread_out = thread_service.search_threads("fastapi", 1, 10, user)
    comment_out = comment_service.search_comments("fastapi", 1, 10, user)

    assert thread_out["total"] == 1
    assert thread_out["items"][0].like_count == 5
    assert thread_out["items"][0].is_liked_by_current_user is True

    assert comment_out["total"] == 1
    assert comment_out["items"][0].like_count == 3
    assert comment_out["items"][0].is_liked_by_current_user is False
