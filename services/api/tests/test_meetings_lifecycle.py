import struct
import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_meeting_lifecycle_endpoints(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Create meeting
    create_resp = await async_client.post(
        "/api/v1/meetings",
        json={
            "title": "Engineering Sprint Sync",
            "platform": "google-meet",
            "meeting_url": "https://meet.google.com/xyz-uvwx-rst",
            "consent_confirmed": True,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    meeting_id = create_resp.json()["data"]["id"]

    # 2. Start meeting
    start_resp = await async_client.post(f"/api/v1/meetings/{meeting_id}/start", headers=headers)
    assert start_resp.status_code == 200
    assert start_resp.json()["data"]["status"] == "active"

    # 3. Pause meeting
    pause_resp = await async_client.post(f"/api/v1/meetings/{meeting_id}/pause", headers=headers)
    assert pause_resp.status_code == 200
    assert pause_resp.json()["data"]["status"] == "paused"

    # 4. Resume meeting
    resume_resp = await async_client.post(f"/api/v1/meetings/{meeting_id}/resume", headers=headers)
    assert resume_resp.status_code == 200
    assert resume_resp.json()["data"]["status"] == "active"

    # 5. Stop meeting
    stop_resp = await async_client.post(f"/api/v1/meetings/{meeting_id}/stop", headers=headers)
    assert stop_resp.status_code == 200
    assert stop_resp.json()["data"]["status"] == "stopped"

    # 6. Complete meeting
    comp_resp = await async_client.post(f"/api/v1/meetings/{meeting_id}/complete", headers=headers)
    assert comp_resp.status_code == 200
    assert comp_resp.json()["data"]["status"] == "completed"


def test_websocket_binary_audio_streaming():
    token = create_access_token({"sub": "user_audio_stream_test"})
    client = TestClient(app)

    with client.websocket_connect(f"/ws/meetings/meet-test-123/audio?token={token}") as ws:
        # 1. Connection ack
        ack = ws.receive_json()
        assert ack["type"] == "connection_ack"
        assert ack["session_id"] == "meet-test-123"

        # 2. Send session_init handshake
        ws.send_json({
            "type": "session_init",
            "meetingId": "meet-test-123",
            "platform": "google-meet"
        })
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # 3. Build Binary Audio Frame:
        # Header: Version(1)=1, SourceID(1)=0 (Tab), Seq(4)=42, Timestamp(8)=1250.0,
        # SampleRate(2)=16000, Channels(1)=1, Encoding(1)=1, SampleCount(4)=100, MLen(1)=13
        meeting_id = b"meet-test-123"
        header = struct.pack(
            ">BBI d HBBIB",
            1,      # Version
            0,      # Source: Tab Audio
            42,     # Sequence Number
            1250.0, # Session relative timestamp ms
            16000,  # 16kHz
            1,      # 1 Channel
            1,      # PCM S16LE
            100,    # 100 samples
            len(meeting_id)
        )
        fake_pcm_samples = b"\x00\x00" * 100 # 200 bytes
        frame_bytes = header + meeting_id + fake_pcm_samples

        # Send binary frame to WebSocket
        ws.send_bytes(frame_bytes)

        # Receive audio_ack or audio_received
        audio_ack = ws.receive_json()
        assert audio_ack["type"] in ("audio_ack", "audio_received")
        assert audio_ack["session_id"] == "meet-test-123"
        assert audio_ack["sourceId"] == 0
        assert audio_ack["sequenceNumber"] == 42
        assert audio_ack["sampleCount"] == 100
        assert "receivedAt" in audio_ack

