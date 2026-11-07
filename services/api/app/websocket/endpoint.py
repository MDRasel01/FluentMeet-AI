from datetime import datetime, timezone
import json
import struct
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security import decode_token
from app.websocket.manager import manager
import logging

logger = logging.getLogger("websocket")
router = APIRouter()

async def handle_websocket_loop(websocket: WebSocket, session_id: str, token: str = None):
    # Verify auth token if provided
    user_id = "anonymous"
    if token:
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = payload["sub"]
    else:
        # In development allow test connection if not strict
        user_id = "dev_user"

    await manager.connect(websocket, session_id=session_id, user_id=user_id)
    
    # Send connection_ack
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
            ws_message = await websocket.receive()
            
            # 1. Handle Binary Audio Stream Frame (Specification Section 12.1)
            if "bytes" in ws_message and ws_message["bytes"]:
                raw_bytes = ws_message["bytes"]
                if len(raw_bytes) >= 23:
                    try:
                        version, source_id, seq_num, ts_ms, sample_rate, channels, encoding, sample_count, m_len = (
                            struct.unpack_from(">BBI d HBBIB", raw_bytes, 0)
                        )
                        offset = 23 + m_len
                        audio_payload = raw_bytes[offset:]

                        # Send audio_ack back to client
                        ack_payload = {
                            "type": "audio_ack",
                            "session_id": session_id,
                            "sourceId": source_id,
                            "sequenceNumber": seq_num,
                            "sampleCount": sample_count,
                            "receivedAt": datetime.now(timezone.utc).isoformat()
                        }
                        await manager.send_personal_message(ack_payload, websocket)
                    except Exception as e:
                        logger.error(f"Error unpacking binary audio frame: {e}")
                continue

            # 2. Handle Text JSON Control Messages
            elif "text" in ws_message and ws_message["text"]:
                raw_data = ws_message["text"]
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
                elif msg_type == "session_init":
                    await manager.send_personal_message(
                        {
                            "type": "session_ready",
                            "session_id": session_id,
                            "status": "ready",
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
                elif msg_type == "session_stop":
                    await manager.send_personal_message(
                        {
                            "type": "session_completed",
                            "session_id": session_id,
                            "status": "completed",
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


@router.websocket("/ws/v1/sessions/{session_id}")
async def websocket_session_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(None)
):
    await handle_websocket_loop(websocket, session_id=session_id, token=token)


@router.websocket("/ws/meetings/{meeting_id}/audio")
async def websocket_meeting_audio_endpoint(
    websocket: WebSocket,
    meeting_id: str,
    token: str = Query(None)
):
    await handle_websocket_loop(websocket, session_id=meeting_id, token=token)
