"""
FluentMeet AI - Step 07 Test Suite: Transcript & Speaker REST Endpoints
Specification: Step 07 - Section 8 & Section 18
"""

import pytest
from httpx import AsyncClient
import app.database.session as app_session_mod
from app.models.transcript import MeetingSpeaker, TranscriptSegment, TranscriptWord, SpeechOverlap

@pytest.mark.asyncio
async def test_transcript_endpoints_lifecycle(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Create a meeting
    meeting_resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Q3 Planning Session", "platform": "google_meet"},
        headers=headers
    )
    assert meeting_resp.status_code == 201
    meeting_id = meeting_resp.json()["data"]["id"]

    # 2. Seed speaker and transcript segments in DB
    async with app_session_mod.AsyncSessionLocal() as db:
        speaker = MeetingSpeaker(
            meeting_id=meeting_id,
            speaker_label="speaker_001",
            display_name="Sarah (Product Lead)",
            source_id=1,
            is_identified=True
        )
        db.add(speaker)
        await db.flush()

        seg1 = TranscriptSegment(
            meeting_id=meeting_id,
            speaker_id=speaker.id,
            source_id=1,
            start_time_ms=0,
            end_time_ms=3000,
            duration_ms=3000,
            text="Let us review the product roadmap for Q3.",
            language="en",
            confidence_score=0.96,
            status="final",
            words_json=[
                {"word": "Let", "start_time_ms": 0, "end_time_ms": 300, "confidence_score": 0.98},
                {"word": "us", "start_time_ms": 310, "end_time_ms": 500, "confidence_score": 0.95},
            ]
        )
        db.add(seg1)

        overlap = SpeechOverlap(
            meeting_id=meeting_id,
            start_time_ms=2500,
            end_time_ms=3000,
            duration_ms=500,
            overlapping_speaker_ids=["speaker_user_me", "speaker_001"],
            confidence_score=0.89
        )
        db.add(overlap)
        await db.commit()
        await db.refresh(speaker)
        await db.refresh(seg1)
        speaker_id = speaker.id
        segment_id = seg1.id

    # 3. GET /api/v1/meetings/{meeting_id}/transcripts
    res_list = await async_client.get(f"/api/v1/meetings/{meeting_id}/transcripts", headers=headers)
    assert res_list.status_code == 200
    data = res_list.json()["data"]
    assert len(data) == 1
    assert data[0]["text"] == "Let us review the product roadmap for Q3."
    assert data[0]["speaker_name"] == "Sarah (Product Lead)"

    # 4. Filter by status
    res_filt = await async_client.get(
        f"/api/v1/meetings/{meeting_id}/transcripts?status=partial",
        headers=headers
    )
    assert res_filt.status_code == 200
    assert len(res_filt.json()["data"]) == 0

    # 5. GET /api/v1/meetings/{meeting_id}/transcripts/{segment_id}
    res_single = await async_client.get(
        f"/api/v1/meetings/{meeting_id}/transcripts/{segment_id}",
        headers=headers
    )
    assert res_single.status_code == 200
    assert res_single.json()["data"]["id"] == segment_id

    # 6. PATCH /api/v1/meetings/{meeting_id}/transcripts/{segment_id} (Manual correction)
    patch_res = await async_client.patch(
        f"/api/v1/meetings/{meeting_id}/transcripts/{segment_id}",
        json={"text": "Let us review the engineering roadmap for Q3."},
        headers=headers
    )
    assert patch_res.status_code == 200
    corrected = patch_res.json()["data"]
    assert corrected["text"] == "Let us review the engineering roadmap for Q3."
    assert corrected["status"] == "corrected"
    assert corrected["revision_number"] == 2

    # 7. GET /api/v1/meetings/{meeting_id}/speakers
    spk_res = await async_client.get(f"/api/v1/meetings/{meeting_id}/speakers", headers=headers)
    assert spk_res.status_code == 200
    speakers = spk_res.json()["data"]
    assert len(speakers) == 1
    assert speakers[0]["speaker_label"] == "speaker_001"

    # 8. PATCH /api/v1/meetings/{meeting_id}/speakers/{speaker_id}
    spk_patch = await async_client.patch(
        f"/api/v1/meetings/{meeting_id}/speakers/{speaker_id}",
        json={"display_name": "Sarah Connor"},
        headers=headers
    )
    assert spk_patch.status_code == 200
    assert spk_patch.json()["data"]["display_name"] == "Sarah Connor"

    # 9. GET /api/v1/meetings/{meeting_id}/overlaps
    ov_res = await async_client.get(f"/api/v1/meetings/{meeting_id}/overlaps", headers=headers)
    assert ov_res.status_code == 200
    overlaps = ov_res.json()["data"]
    assert len(overlaps) == 1
    assert overlaps[0]["duration_ms"] == 500

@pytest.mark.asyncio
async def test_transcript_unauthorized_access(async_client: AsyncClient):
    # Attempting to fetch transcripts without authorization header
    res = await async_client.get("/api/v1/meetings/some-random-id/transcripts")
    assert res.status_code in (401, 403)
