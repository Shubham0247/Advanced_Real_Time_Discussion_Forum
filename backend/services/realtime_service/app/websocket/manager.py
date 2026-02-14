from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, thread_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(thread_id, []).append(websocket)

    def disconnect(self, thread_id: str, websocket: WebSocket):
        self.active_connections[thread_id].remove(websocket)
        if not self.active_connections[thread_id]:
            del self.active_connections[thread_id]

    async def broadcast(self, thread_id: str, message: dict):
        print("Broadcasting to thread:", thread_id)
        print("Active connections:", self.active_connections.keys())

        connections = self.active_connections.get(thread_id, [])
        print("Connections found:", len(connections))

        for connection in connections:
            await connection.send_json(message)

manager = ConnectionManager()