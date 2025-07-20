from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected for session {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected for session {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            disconnected_connections = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to {session_id}: {e}")
                    disconnected_connections.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected_connections:
                self.disconnect(connection, session_id)

    async def send_transcription_update(self, session_id: str, status: str, data: dict = None):
        message = {
            "type": "transcription_update",
            "session_id": session_id,
            "status": status,
            "timestamp": data.get("timestamp") if data else None,
            "data": data or {}
        }
        await self.send_personal_message(message, session_id)

    async def send_progress_update(self, session_id: str, progress: int, stage: str, details: str = None):
        message = {
            "type": "progress_update",
            "session_id": session_id,
            "progress": progress,
            "stage": stage,
            "details": details,
            "timestamp": None  # Could add current timestamp
        }
        await self.send_personal_message(message, session_id)

    async def send_error_notification(self, session_id: str, error: str, error_code: str = None):
        message = {
            "type": "error",
            "session_id": session_id,
            "error": error,
            "error_code": error_code,
            "timestamp": None  # Could add current timestamp
        }
        await self.send_personal_message(message, session_id)

manager = ConnectionManager()