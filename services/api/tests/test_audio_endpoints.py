"""
FluentMeet AI - Step 06 Test Suite: Audio REST Endpoints
Specification: Step 06 - Section 18 & 21
"""

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_audio_endpoints_lifecycle(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Create a meeting first
    meeting_resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Test Audio Meeting", "platform": "google_meet"},
        headers=headers
    )
    assert meeting_resp.status_code == 201
    meeting_id = meeting_resp.json()["data"]["id"]

    # 2. Register Audio Stream for Source 0 (Remote Tab)
    stream0_resp = await async_client.post(
        f"/api/v1/meetings/{meeting_id}/audio-streams",
        json={"source_id": 0, "codec": "pcm_s16le", "sample_rate": 16000, "channels": 1},
        headers=headers
    )
    assert stream0_resp.status_code == 200
    stream0 = stream0_resp.json()["data"]
    assert stream0["meeting_id"] == meeting_id
    assert stream0["source_id"] == 0
    stream0_id = stream0["id"]

    # 3. Register Audio Stream for Source 1 (Local Mic)
    stream1_resp = await async_client.post(
        f"/api/v1/meetings/{meeting_id}/audio-streams",
        json={"source_id": 1, "codec": "pcm_s16le", "sample_rate": 16000, "channels": 1},
        headers=headers
    )
    assert stream1_resp.status_code == 200
    stream1 = stream1_resp.json()["data"]
    assert stream1["source_id"] == 1

    # 4. List streams for meeting
    list_resp = await async_client.get(f"/api/v1/meetings/{meeting_id}/audio-streams", headers=headers)
    assert list_resp.status_code == 200
    streams = list_resp.json()["data"]
    assert len(streams) == 2

    # 5. Get stream by ID
    get_stream_resp = await async_client.get(f"/api/v1/audio-streams/{stream0_id}", headers=headers)
    assert get_stream_resp.status_code == 200
    assert get_stream_resp.json()["data"]["id"] == stream0_id

    # 6. Get meeting audio status
    status_resp = await async_client.get(f"/api/v1/meetings/{meeting_id}/audio-status", headers=headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()["data"]
    assert status_data["meeting_id"] == meeting_id

    # 7. Get meeting audio quality
    quality_resp = await async_client.get(f"/api/v1/meetings/{meeting_id}/audio-quality", headers=headers)
    assert quality_resp.status_code == 200

    # 8. Close audio stream
    close_resp = await async_client.post(f"/api/v1/audio-streams/{stream0_id}/close", headers=headers)
    assert close_resp.status_code == 200
    assert close_resp.json()["data"]["status"] == "closed"
