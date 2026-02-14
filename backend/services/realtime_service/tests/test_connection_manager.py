import asyncio

from backend.services.realtime_service.app.websocket.manager import ConnectionManager


def test_connect_broadcast_disconnect_flow():
    manager = ConnectionManager()

    class FakeWebSocket:
        def __init__(self):
            self.accepted = False
            self.messages = []

        async def accept(self):
            self.accepted = True

        async def send_json(self, payload):
            self.messages.append(payload)

    ws = FakeWebSocket()
    payload = {"event": "thread.updated"}

    asyncio.run(manager.connect("thread-1", ws))
    asyncio.run(manager.broadcast("thread-1", payload))
    manager.disconnect("thread-1", ws)

    assert ws.accepted is True
    assert ws.messages == [payload]
    assert "thread-1" not in manager.active_connections


def test_broadcast_to_unknown_key_is_noop():
    manager = ConnectionManager()
    asyncio.run(manager.broadcast("missing-thread", {"event": "noop"}))
    assert manager.active_connections == {}
