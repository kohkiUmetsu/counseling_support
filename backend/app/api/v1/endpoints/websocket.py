from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for heartbeat/keepalive
            await websocket.send_text(f"Session {session_id} connected")
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(websocket, session_id)