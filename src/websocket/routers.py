from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.db import LocalSession
from src.dependencies.websocket_is_authenticated import websocket_is_authenticated
from src.websocket.manager import manager

websocket_routes = APIRouter(prefix="/ws", tags=["WebSockets"])


@websocket_routes.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    db = LocalSession()

    user = websocket_is_authenticated(websocket, db)

    if not user:
        await websocket.close(code=1008)
        db.close()
        return

    await manager.connect(user.id, websocket)

    try:
        while True:
            message = await websocket.receive_text()

            await manager.send_to_user(
                user_id=user.id, message=f"User {user.id} received: {message}"
            )

    except WebSocketDisconnect:
        manager.disconnect(user.id)

    finally:
        db.close()
