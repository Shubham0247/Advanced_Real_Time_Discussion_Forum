from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from backend.services.discussion_service.app.services.comment_service import CommentService


def _make_comment(author_id, thread_id=None, parent_id=None):
    return SimpleNamespace(
        id=uuid4(),
        content="hello",
        author_id=author_id,
        thread_id=thread_id or uuid4(),
        parent_id=parent_id,
        replies=[],
    )


def test_create_reply_emits_comment_replied_event(monkeypatch):
    db = SimpleNamespace()
    service = CommentService(db)

    thread_id = uuid4()
    parent_author = uuid4()
    reply_author = uuid4()
    parent_comment = _make_comment(parent_author, thread_id=thread_id)
    created_comment = _make_comment(reply_author, thread_id=thread_id, parent_id=parent_comment.id)

    class FakeRepo:
        def get_by_id(self, cid):
            assert cid == parent_comment.id
            return parent_comment

        def create(self, _comment):
            return created_comment

    service.repo = FakeRepo()
    service.thread_service = SimpleNamespace(get_thread=lambda _tid: SimpleNamespace(is_locked=False))

    published = []
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.publish_event",
        lambda **kwargs: published.append(kwargs),
    )
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.extract_mentioned_usernames",
        lambda _text: set(),
    )
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.publish_mention_events_for_usernames",
        lambda *_args, **_kwargs: None,
    )

    service.create_comment(thread_id, "reply text", reply_author, parent_comment.id)

    events = {(e["channel"], e["event"]) for e in published}
    assert ("thread_updates", "comment.created") in events
    assert ("discussion_events", "comment.replied") in events


def test_create_reply_to_self_does_not_emit_comment_replied(monkeypatch):
    db = SimpleNamespace()
    service = CommentService(db)

    thread_id = uuid4()
    same_user = uuid4()
    parent_comment = _make_comment(same_user, thread_id=thread_id)
    created_comment = _make_comment(same_user, thread_id=thread_id, parent_id=parent_comment.id)

    class FakeRepo:
        def get_by_id(self, _cid):
            return parent_comment

        def create(self, _comment):
            return created_comment

    service.repo = FakeRepo()
    service.thread_service = SimpleNamespace(get_thread=lambda _tid: SimpleNamespace(is_locked=False))

    published = []
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.publish_event",
        lambda **kwargs: published.append(kwargs),
    )
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.extract_mentioned_usernames",
        lambda _text: set(),
    )
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.publish_mention_events_for_usernames",
        lambda *_args, **_kwargs: None,
    )

    service.create_comment(thread_id, "reply text", same_user, parent_comment.id)
    assert all(e["event"] != "comment.replied" for e in published)


def test_moderator_can_update_and_delete_any_comment(monkeypatch):
    db = SimpleNamespace()
    service = CommentService(db)
    other_user_id = uuid4()
    moderator_id = uuid4()
    comment = _make_comment(other_user_id)
    comment.content = "old"

    class FakeRepo:
        def __init__(self):
            self.deleted = False

        def get_by_id(self, _cid):
            return comment

        def update(self, c):
            return c

        def soft_delete(self, c):
            self.deleted = True
            return c

    repo = FakeRepo()
    service.repo = repo

    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.publish_event",
        lambda **_kwargs: None,
    )
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.extract_mentioned_usernames",
        lambda _text: set(),
    )
    monkeypatch.setattr(
        "backend.services.discussion_service.app.services.comment_service.publish_mention_events_for_usernames",
        lambda *_args, **_kwargs: None,
    )

    moderator = SimpleNamespace(id=moderator_id, roles=[SimpleNamespace(name="moderator")])
    updated = service.update_comment(comment.id, "new", moderator)
    deleted = service.delete_comment(comment.id, moderator)

    assert updated.content == "new"
    assert deleted is comment
    assert repo.deleted is True


def test_non_owner_member_cannot_update_or_delete_comment():
    db = SimpleNamespace()
    service = CommentService(db)
    owner_id = uuid4()
    member_id = uuid4()
    comment = _make_comment(owner_id)
    service.repo = SimpleNamespace(get_by_id=lambda _cid: comment)
    member = SimpleNamespace(id=member_id, roles=[SimpleNamespace(name="member")])

    with pytest.raises(HTTPException) as e1:
        service.update_comment(comment.id, "new", member)
    assert e1.value.status_code == 403

    with pytest.raises(HTTPException) as e2:
        service.delete_comment(comment.id, member)
    assert e2.value.status_code == 403
