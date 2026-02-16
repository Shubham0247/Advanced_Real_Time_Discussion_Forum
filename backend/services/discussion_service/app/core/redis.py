import redis
import json
import os


def get_redis_port() -> int:
    try:
        return int(os.getenv("REDIS_PORT", "6379"))
    except ValueError:
        return 6379

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=get_redis_port(),
    decode_responses=True
)

def publish_thread_event(thread_id: str, event_type: str, data: dict):
    redis_client.publish(
        "thread_updates",
        json.dumps({
            "thread_id": thread_id,
            "type": event_type,
            "data": data
        })
    )
