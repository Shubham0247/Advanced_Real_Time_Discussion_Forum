import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
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
