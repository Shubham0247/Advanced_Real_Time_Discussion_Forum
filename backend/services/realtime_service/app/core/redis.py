import redis.asyncio as redis
import json
from backend.services.realtime_service.app.websocket.manager import manager

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

async def start_redis_listener():
    print("Starting Redis listener...")
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("thread_updates", "user_notifications")
    print("Subscribed to thread_updates and user_notifications")

    async for message in pubsub.listen():
        print("Redis message received:", message)
        if message["type"] == "message":
            data = json.loads(message["data"])
            channel = message.get("channel")

            if channel == "thread_updates":
                thread_id = data.get("thread_id")
                if thread_id:
                    await manager.broadcast(thread_id, data)
                # Also broadcast to the global feed room so the
                # HomePage can pick up likes/updates in real-time.
                await manager.broadcast("__feed__", data)

            elif channel == "user_notifications":
                user_id = data.get("user_id")
                if user_id:
                    await manager.broadcast(user_id, data)

