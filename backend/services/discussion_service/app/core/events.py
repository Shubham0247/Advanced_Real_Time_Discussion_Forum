import redis
import json
from datetime import datetime, timezone
import uuid

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


def publish_event(
    channel: str,
    event: str,
    thread_id: str,
    actor_id: str,
    payload: dict,
):
    message = {
        "event_id": str(uuid.uuid4()),
        "event": event,
        "thread_id": thread_id,
        "actor_id": actor_id,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    redis_client.publish(channel, json.dumps(message))