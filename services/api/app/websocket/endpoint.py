"""
FluentMeet AI - Real-Time Audio Streaming WebSocket Endpoint
Specification: Step 06 - Section 5, 6, 7, 12, 13, 16
"""

from datetime import datetime, timezone
import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.core.config import settings
from app.core.security import decode_token
from app.websocket.manager import manager
from app.database import session as db_session
from app.audio.service import audio_ingestion_service
from app.audio.protocol import ProtocolValidationError
from app.audio.validator import AudioValidationError
from app.audio.buffering.buffer_manager import BufferOverflowError
from app.audio.metering import AudioUsageMeter

logger = logging.getLogger("websocket.audio")
router = APIRouter()

def validate_origin(websocket: WebSocket) -> bool:
    """
    Validates the WebSocket handshake Origin header against allowed patterns.
    Supports localhost, custom domains, and Chrome Extension schemes.
    """
    origin = websocket.headers.get("origin")
    if not origin:
        # Development / CLI clients or test fixtures may not send Origin
        return True

    for allowed in settings.CORS_ORIGINS:
        if allowed == "*":
            return True
        if allowed.endswith("*") and origin.startswith(allowed[:-1]):
            return True
        if origin == allowed:
            return True

    return False

async def handle_websocket_loop(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = None,
    org_id: Optional[str] = None
):
    # 1. Enforce Origin Validation (Security - Section 20)
    if not validate_origin(websocket):
        logger.warning(f"Rejected WebSocket connection from unauthorized origin: {websocket.headers.get('origin')}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Authenticate User & Tenant Context (Section 6 & 20)
    user_id = "anonymous"
    tenant_org_id = org_id

    if token:
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            logger.warning("Rejected WebSocket connection due to invalid/expired token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = payload["sub"]
        if not tenant_org_id and "org_id" in payload:
            tenant_org_id = payload["org_id"]
    else:
        # Enforce authentication in non-development/non-testing environments (DEF-001)
        if settings.APP_ENV not in ("development", "testing"):
            logger.warning("Rejected unauthenticated WebSocket connection in production")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        # Development fallback if running locally
        user_id = "dev_user"

    await manager.connect(websocket, session_id=session_id, user_id=user_id)

    # Send initial connection acknowledgement
    await manager.send_personal_message(
        {
            "type": "connection_ack",
            "session_id": session_id,
            "user_id": user_id,
            "organization_id": tenant_org_id,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "status": "ready"
        },
        websocket
    )

    try:
        while True:
            ws_message = await websocket.receive()

            # -------------------------------------------------------------
            # Branch A: Handle Binary Audio Stream Frame (Sections 7, 8, 12, 13)
            # -------------------------------------------------------------
            if "bytes" in ws_message and ws_message["bytes"]:
                raw_bytes = ws_message["bytes"]
                async with db_session.AsyncSessionLocal() as db:
                    try:
                        # Ingest through central pipeline:
                        # Protocol decode -> Validation -> Sequence/Gap -> Drift -> Buffering -> Segment/Storage/DB/Redis
                        level1_ack, level2_ack = await audio_ingestion_service.ingest_binary_packet(
                            raw_bytes=raw_bytes,
                            session_id=session_id,
                            organization_id=tenant_org_id,
                            db=db
                        )

                        # Deliver Level 1 ACK (audio_received)
                        await manager.send_personal_message(level1_ack, websocket)

                        # Deliver Level 2 ACK (audio_persisted) if 1-5s segment was flushed
                        if level2_ack:
                            await manager.send_personal_message(level2_ack, websocket)
                            # Record metered usage
                            await AudioUsageMeter.record_usage(
                                db=db,
                                user_id=user_id,
                                organization_id=tenant_org_id,
                                meeting_id=session_id,
                                source_id=level2_ack["sourceId"],
                                duration_ms=level2_ack["durationMs"],
                                storage_bytes=level2_ack["sampleCount"] * 2,
                                processed_bytes=level2_ack["sampleCount"] * 2,
                            )

                    except (ProtocolValidationError, AudioValidationError) as err:
                        logger.error(f"Validation failure on audio stream: {err}")
                        await manager.send_personal_message(
                            {
                                "type": "audio_error",
                                "code": getattr(err, "code", "VALIDATION_ERROR"),
                                "message": str(err),
                                "session_id": session_id
                            },
                            websocket
                        )
                    except BufferOverflowError as err:
                        logger.error(f"Buffer backpressure overflow: {err}")
                        await manager.send_personal_message(
                            {
                                "type": "audio_backpressure",
                                "code": "BUFFER_OVERFLOW",
                                "message": str(err),
                                "session_id": session_id
                            },
                            websocket
                        )
                    except Exception as err:
                        logger.error(f"Internal audio processing error: {err}", exc_info=True)
                        await manager.send_personal_message(
                            {
                                "type": "audio_error",
                                "code": "INGESTION_INTERNAL_ERROR",
                                "message": "Failed to process audio chunk",
                                "session_id": session_id
                            },
                            websocket
                        )
                continue

            # -------------------------------------------------------------
            # Branch B: Handle JSON Control Messages (Section 6 & 16)
            # -------------------------------------------------------------
            elif "text" in ws_message and ws_message["text"]:
                raw_data = ws_message["text"]
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    await manager.send_personal_message(
                        {"type": "error", "message": "Invalid JSON control payload"},
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

                elif msg_type == "session_stop":
                    logger.info(f"Received session_stop for {session_id}. Flushing remaining audio buffers...")
                    async with db_session.AsyncSessionLocal() as db:
                        flushed_acks = await audio_ingestion_service.flush_remaining_audio(
                            session_id=session_id,
                            organization_id=tenant_org_id,
                            db=db
                        )
                        for persisted_ack in flushed_acks:
                            await manager.send_personal_message(persisted_ack, websocket)
                            await AudioUsageMeter.record_usage(
                                db=db,
                                user_id=user_id,
                                organization_id=tenant_org_id,
                                meeting_id=session_id,
                                source_id=persisted_ack["sourceId"],
                                duration_ms=persisted_ack["durationMs"],
                                storage_bytes=persisted_ack["sampleCount"] * 2,
                                processed_bytes=persisted_ack["sampleCount"] * 2,
                            )

                    await manager.send_personal_message(
                        {
                            "type": "session_completed",
                            "session_id": session_id,
                            "flushed_segments_count": len(flushed_acks),
                            "status": "completed",
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
        logger.info(f"WebSocket client disconnected: session={session_id}. Flushing uncommitted buffers...")
        try:
            async with db_session.AsyncSessionLocal() as db:
                await audio_ingestion_service.flush_remaining_audio(
                    session_id=session_id,
                    organization_id=tenant_org_id,
                    db=db
                )
        except Exception as e:
            logger.error(f"Error flushing audio on disconnect: {e}")

    except Exception as e:
        manager.disconnect(websocket)
        logger.error(f"Unhandled WebSocket error: {e}")


@router.websocket("/ws/v1/sessions/{session_id}")
async def websocket_session_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None)
):
    await handle_websocket_loop(websocket, session_id=session_id, token=token, org_id=org_id)


@router.websocket("/ws/meetings/{meeting_id}/audio")
async def websocket_meeting_audio_endpoint(
    websocket: WebSocket,
    meeting_id: str,
    token: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None)
):
    await handle_websocket_loop(websocket, session_id=meeting_id, token=token, org_id=org_id)


@router.websocket("/ws/meetings/{meeting_id}/transcripts")
async def websocket_meeting_transcripts_endpoint(
    websocket: WebSocket,
    meeting_id: str,
    token: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None)
):
    await handle_websocket_loop(websocket, session_id=meeting_id, token=token, org_id=org_id)

