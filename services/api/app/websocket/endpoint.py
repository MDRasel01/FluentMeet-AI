from datetime import datetime, timezone
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security import decode_token
from app.websocket.manager import manager
import logging

logger = logging.getLogger("websocket")
router = APIRouter()

@router.websocket("/ws/v1/sessions/{session_id}")
async def websocket_session_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(None)
):
    # Verify auth token if provided
    user_id = "anonymous"
    if token:
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = payload["sub"]
    elif not token:
        # In development allow test connection if not strict, or reject
        user_id = "dev_user"

    await manager.connect(websocket, session_id=session_id, user_id=user_id)
    
    # Send ack
    await manager.send_personal_message(
        {
            "type": "connection_ack",
            "session_id": session_id,
            "user_id": user_id,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "status": "ready"
        },
        websocket
    )

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON payload"},
                    websocket
                )
                continue

            msg_type = data.get("type")
            if msg_type == "ping":
                await manager.send_personal_message(
                    {
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    websocket
                )
            elif msg_type == "test_echo":
                await manager.send_personal_message(
                    {
                        "type": "test_echo_reply",
                        "data": data.get("data"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    websocket
                )
            elif msg_type == "broadcast_event":
                await manager.broadcast(
                    {
                        "type": "broadcast_event",
                        "sender_id": user_id,
                        "data": data.get("data"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    session_id=session_id
                )
            else:
                # Handle future event types (audio chunks metadata, coaching signals)
                await manager.send_personal_message(
                    {
                        "type": "ack",
                        "event": msg_type,
                        "status": "received"
                    },
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket client disconnected cleanly: session={session_id}")
    except Exception as e:
        manager.disconnect(websocket)
        logger.error(f"WebSocket error: {e}")

