from types import SimpleNamespace
from uuid import uuid4

from backend.services.discussion_service.app.core import mentions


def test_extract_mentioned_usernames_deduplicates_and_filters_short_names():
    text = "Hi @alice and @bob and again @alice, but not @ab"
    found = mentions.extract_mentioned_usernames(text)
    assert found == {"alice", "bob"}


def test_publish_mentions_skips_actor_and_emits_for_others(monkeypatch):
    actor_id = uuid4()
    alice_id = uuid4()
    bob_id = uuid4()

    fake_users = [
        SimpleNamespace(id=alice_id, username="alice"),
        SimpleNamespace(id=actor_id, username="me"),
        SimpleNamespace(id=bob_id, username="bob"),
    ]

    class FakeDB:
        def scalars(self, _query):
            return fake_users

    published = []

    def fake_publish_event(**kwargs):
        published.append(kwargs)

    monkeypatch.setattr(mentions, "publish_event", fake_publish_event)

    mentions.publish_mention_events_for_usernames(
        FakeDB(),
        usernames={"alice", "me", "bob"},
        actor_id=actor_id,
        thread_id=uuid4(),
        source_type="comment",
        source_id=uuid4(),
        preview="hello",
    )

    assert len(published) == 2
    mentioned_ids = {evt["payload"]["mentioned_user_id"] for evt in published}
    assert mentioned_ids == {str(alice_id), str(bob_id)}


def test_publish_mentions_no_usernames_no_publish(monkeypatch):
    class FakeDB:
        def scalars(self, _query):
            return []

    published = []
    monkeypatch.setattr(mentions, "publish_event", lambda **kwargs: published.append(kwargs))

    mentions.publish_mention_events_for_usernames(
        FakeDB(),
        usernames=set(),
        actor_id=uuid4(),
        thread_id=uuid4(),
        source_type="thread",
        source_id=uuid4(),
        preview="",
    )

    assert published == []
