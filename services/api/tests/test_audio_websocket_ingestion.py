"""
FluentMeet AI - Step 06 Test Suite: WebSocket Audio Ingestion & Two-Tier ACKs
Specification: Step 06 - Section 12, 13, 16 & 21 (REQ-ING-001, REQ-ING-002, REQ-ING-016)
"""

import pytest
import numpy as np
from starlette.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.audio.protocol import BinaryAudioProtocol, AudioPacket

def make_binary_chunk(meeting_id: str, source_id: int, seq: int, ts_ms: float, duration_ms: int = 1000) -> bytes:
    sample_count = int(16000 * (duration_ms / 1000.0))
    t = np.linspace(0, duration_ms / 1000.0, sample_count, endpoint=False)
    pcm = (np.sin(2 * np.pi * 440 * t) * 12000).astype(np.int16).tobytes()
    packet = AudioPacket(
        version=1,
        source_id=source_id,
        sequence_number=seq,
        session_relative_timestamp_ms=ts_ms,
        sample_rate=16000,
        channels=1,
        encoding=1,
        sample_count=sample_count,
        meeting_id=meeting_id,
        pcm_payload=pcm,
    )
    return BinaryAudioProtocol.encode(packet)

class TestWebSocketAudioIngestion:
    def test_websocket_binary_audio_two_tier_ack(self):
        meeting_id = "ws-test-meeting-1"
        token = create_access_token({"sub": "user-test-ws", "org_id": "org-test-ws"})
        client = TestClient(app)

        with client.websocket_connect(f"/ws/meetings/{meeting_id}/audio?token={token}") as ws:
            # 1. Verify connection_ack
            conn_ack = ws.receive_json()
            assert conn_ack["type"] == "connection_ack"
            assert conn_ack["session_id"] == meeting_id

            # 2. Send 1st chunk (1000ms, seq=1) -> Expect Level 1 ACK (audio_received)
            raw_chunk_1 = make_binary_chunk(meeting_id, source_id=0, seq=1, ts_ms=0.0, duration_ms=1000)
            ws.send_bytes(raw_chunk_1)

            l1_ack_1 = ws.receive_json()
            assert l1_ack_1["type"] == "audio_received"
            assert l1_ack_1["status"] == "accepted"
            assert l1_ack_1["sourceId"] == 0
            assert l1_ack_1["sequenceNumber"] == 1

            # 3. Send 2nd chunk (1000ms, seq=2)
            raw_chunk_2 = make_binary_chunk(meeting_id, source_id=0, seq=2, ts_ms=1000.0, duration_ms=1000)
            ws.send_bytes(raw_chunk_2)

            l1_ack_2 = ws.receive_json()
            assert l1_ack_2["type"] == "audio_received"
            assert l1_ack_2["sequenceNumber"] == 2

            # 4. Send 3rd chunk (1000ms, seq=3) -> Crosses 3000ms threshold -> Expect Level 1 AND Level 2 ACK!
            raw_chunk_3 = make_binary_chunk(meeting_id, source_id=0, seq=3, ts_ms=2000.0, duration_ms=1000)
            ws.send_bytes(raw_chunk_3)

            l1_ack_3 = ws.receive_json()
            assert l1_ack_3["type"] == "audio_received"
            assert l1_ack_3["sequenceNumber"] == 3

            # Expect Level 2 ACK (audio_persisted)
            l2_ack = ws.receive_json()
            assert l2_ack["type"] == "audio_persisted"
            assert l2_ack["sourceId"] == 0
            assert l2_ack["durationMs"] == 3000
            assert l2_ack["sampleCount"] == 48000
            assert "checksum" in l2_ack
            assert "storageKey" in l2_ack

    def test_websocket_session_stop_flushes_remaining_buffer(self):
        meeting_id = "ws-test-meeting-stop"
        token = create_access_token({"sub": "user-test-stop"})
        client = TestClient(app)

        with client.websocket_connect(f"/ws/meetings/{meeting_id}/audio?token={token}") as ws:
            ws.receive_json()  # connection_ack

            # Send 1 chunk of 1500ms (does not cross 3000ms)
            chunk = make_binary_chunk(meeting_id, source_id=1, seq=1, ts_ms=0.0, duration_ms=1500)
            ws.send_bytes(chunk)
            l1_ack = ws.receive_json()
            assert l1_ack["type"] == "audio_received"

            # Client sends session_stop
            ws.send_json({"type": "session_stop"})

            # Should flush partial buffer and return audio_persisted before session_completed
            msg1 = ws.receive_json()
            assert msg1["type"] == "audio_persisted"
            assert msg1["sourceId"] == 1
            assert msg1["durationMs"] == 1500

            msg2 = ws.receive_json()
            assert msg2["type"] == "session_completed"
            assert msg2["flushed_segments_count"] == 1
            assert msg2["status"] == "completed"
