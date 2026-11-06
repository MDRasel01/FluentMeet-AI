from typing import Dict, List, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger("websocket")

class ConnectionManager:
    def __init__(self):
        # session_id -> list of active WebSockets
        self.active_sessions: Dict[str, List[WebSocket]] = {}
        # websocket -> metadata dict
        self.connection_meta: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        await websocket.accept()
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = []
        self.active_sessions[session_id].append(websocket)
        self.connection_meta[websocket] = {
            "session_id": session_id,
            "user_id": user_id,
        }
        logger.info(f"WebSocket client connected. session={session_id}, user={user_id}")

    def disconnect(self, websocket: WebSocket):
        meta = self.connection_meta.pop(websocket, None)
        if meta:
            session_id = meta["session_id"]
            if session_id in self.active_sessions:
                if websocket in self.active_sessions[session_id]:
                    self.active_sessions[session_id].remove(websocket)
                if not self.active_sessions[session_id]:
                    del self.active_sessions[session_id]
            logger.info(f"WebSocket client disconnected. session={session_id}, user={meta.get('user_id')}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict, session_id: str):
        if session_id in self.active_sessions:
            payload = json.dumps(message)
            for connection in self.active_sessions[session_id]:
                try:
                    await connection.send_text(payload)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")

manager = ConnectionManager()

