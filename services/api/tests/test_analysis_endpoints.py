"""
FluentMeet AI - Step 08 REST API Integration Tests: Analysis Endpoints
"""

import pytest
from httpx import AsyncClient
import app.database.session as app_session_mod
from app.models.transcript import MeetingSpeaker, TranscriptSegment


@pytest.mark.asyncio
async def test_analysis_endpoints_full_cycle(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Create meeting
    meeting_resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Client Strategy Workshop", "platform": "google_meet"},
        headers=headers,
    )
    assert meeting_resp.status_code == 201
    meeting_id = meeting_resp.json()["data"]["id"]

    # 2. Seed speaker and transcript segments (> 50 words)
    async with app_session_mod.AsyncSessionLocal() as db:
        speaker = MeetingSpeaker(
            meeting_id=meeting_id,
            speaker_label="speaker_user_me",
            display_name="Test Host",
            source_id=0,
            is_identified=True,
        )
        db.add(speaker)
        await db.flush()

        phrases = [
            "Welcome everyone to this client strategy workshop where we evaluate quarterly milestones.",
            "Our primary objective today is to review the proposal requirements and ensure alignment across all teams.",
            "We have completed the backend infrastructure and resolved the critical database bottlenecks.",
            "However, we should discuss about the budget allocation and timeline for the mobile application rollout.",
            "So basically we are ready to proceed with user acceptance testing starting next Monday morning.",
            "Please feel free to share any feedback or questions regarding our proposed deployment roadmap.",
        ]

        t = 0
        for p in phrases:
            db.add(
                TranscriptSegment(
                    meeting_id=meeting_id,
                    speaker_id=speaker.id,
                    source_id=0,
                    start_time_ms=t,
                    end_time_ms=t + 4000,
                    duration_ms=4000,
                    text=p,
                    language="en",
                    status="final",
                    confidence_score=0.97,
                )
            )
            t += 4500
        await db.commit()

    # 3. POST /api/v1/meetings/{id}/analysis (Trigger)
    trigger_resp = await async_client.post(
        f"/api/v1/meetings/{meeting_id}/analysis",
        json={"force_reanalyze": False},
        headers=headers,
    )
    assert trigger_resp.status_code == 200
    trigger_data = trigger_resp.json()["data"]
    assert trigger_data["status"] == "completed"
    session_id = trigger_data["id"]
    assert len(trigger_data["participants"]) == 1
    participant_summary = trigger_data["participants"][0]
    participant_analysis_id = participant_summary["id"]
    assert participant_summary["overall_score"] is not None

    # 4. Idempotency test: POST again without force returns existing session
    idempotent_resp = await async_client.post(
        f"/api/v1/meetings/{meeting_id}/analysis",
        json={"force_reanalyze": False},
        headers=headers,
    )
    assert idempotent_resp.status_code == 200
    assert idempotent_resp.json()["data"]["id"] == session_id

    # 5. GET /api/v1/analysis/{id}/status
    status_resp = await async_client.get(
        f"/api/v1/analysis/{session_id}/status",
        headers=headers,
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["data"]["status"] == "completed"

    # 6. GET /api/v1/analysis/{id}
    session_resp = await async_client.get(
        f"/api/v1/analysis/{session_id}",
        headers=headers,
    )
    assert session_resp.status_code == 200
    session_data = session_resp.json()["data"]
    assert session_data["id"] == session_id
    assert len(session_data["participants"]) == 1

    # 7. GET /api/v1/analysis/{id}/participants/{participant_analysis_id} (Detailed)
    detail_resp = await async_client.get(
        f"/api/v1/analysis/{session_id}/participants/{participant_analysis_id}",
        headers=headers,
    )
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()["data"]
    assert detail_data["id"] == participant_analysis_id
    assert len(detail_data["category_scores"]) >= 6
    assert len(detail_data["fluency_metrics"]) >= 4
    assert len(detail_data["recommendations"]) >= 1

    # 8. GET /api/v1/participants/{speaker_label}/progress
    progress_resp = await async_client.get(
        f"/api/v1/participants/speaker_user_me/progress",
        headers=headers,
    )
    assert progress_resp.status_code == 200
    progress_data = progress_resp.json()["data"]
    assert progress_data["speaker_label"] == "speaker_user_me"
    assert len(progress_data["history"]) >= 1
    assert progress_data["history"][0]["overall_score"] is not None

    # 9. GET /api/v1/participants/{speaker_label}/recommendations
    recs_resp = await async_client.get(
        f"/api/v1/participants/speaker_user_me/recommendations",
        headers=headers,
    )
    assert recs_resp.status_code == 200
    recs_data = recs_resp.json()["data"]
    assert len(recs_data) >= 1
    assert recs_data[0]["actionable_suggestion"] != ""

