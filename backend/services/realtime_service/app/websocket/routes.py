from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from backend.services.realtime_service.app.websocket.manager import manager
import jwt
from datetime import datetime, timezone
from backend.services.realtime_service.app.core.config import settings


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"

router = APIRouter()


def _validate_ws_token(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if not token:
        return None

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    if payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    return user_id


@router.websocket("/ws/threads/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    try:
        user_id = _validate_ws_token(websocket)
        if not user_id:
            raise jwt.InvalidTokenError

    except jwt.ExpiredSignatureError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    except jwt.InvalidTokenError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # If valid
    await manager.connect(thread_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(thread_id, websocket)


@router.websocket("/ws/feed")
async def feed_websocket_endpoint(websocket: WebSocket):
    """Global feed — broadcasts all thread_updates (likes, new comments, etc.)."""
    try:
        user_id = _validate_ws_token(websocket)
        if not user_id:
            raise jwt.InvalidTokenError
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect("__feed__", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("__feed__", websocket)


@router.websocket("/ws/notifications")
async def notifications_websocket_endpoint(websocket: WebSocket):
    try:
        user_id = _validate_ws_token(websocket)
        if not user_id:
            raise jwt.InvalidTokenError

    except jwt.ExpiredSignatureError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    except jwt.InvalidTokenError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(str(user_id), websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(str(user_id), websocket)
