import json

from backend.services.discussion_service.app.core import events


def test_publish_event_serializes_expected_payload(monkeypatch):
    published = []

    class FakeRedis:
        def publish(self, channel, message):
            published.append((channel, message))

    monkeypatch.setattr(events, "redis_client", FakeRedis())

    events.publish_event(
        channel="discussion_events",
        event="mention",
        thread_id="t1",
        actor_id="u1",
        payload={"k": "v"},
    )

    assert len(published) == 1
    channel, message = published[0]
    data = json.loads(message)
    assert channel == "discussion_events"
    assert data["event"] == "mention"
    assert data["thread_id"] == "t1"
    assert data["actor_id"] == "u1"
    assert "event_id" in data
    assert "timestamp" in data
