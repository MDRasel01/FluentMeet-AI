"""
FluentMeet AI - Step 10 Integration Tests: Historical Progress Service
Tests multi-meeting trajectory tracking, baseline thresholds, and recurring patterns.
"""

import pytest
from httpx import AsyncClient
import app.database.session as app_session_mod
from app.models.base import Meeting, MeetingParticipant
from app.models.report import ReportSnapshot
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_historical_progress_trajectory(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    user_id = auth_token["user_id"]

    participant_id = "test-participant-history-1"

    # Seed 3 meetings and reports spaced across days
    async with app_session_mod.AsyncSessionLocal() as db:
        base_time = datetime.now(timezone.utc) - timedelta(days=10)

        for i, score in enumerate([72.0, 78.0, 84.0]):
            meet = Meeting(
                title=f"Standup Session #{i+1}",
                platform="google_meet",
                user_id=user_id,
            )
            db.add(meet)
            await db.flush()

            part = MeetingParticipant(
                id=participant_id if i == 0 else f"{participant_id}_{i}",
                meeting_id=meet.id,
                name="Bob Progress",
            )
            db.add(part)
            await db.flush()

            snapshot = ReportSnapshot(
                meeting_id=meet.id,
                report_type="individual_participant",
                participant_id=participant_id,
                speaker_label="speaker_bob",
                report_version=1,
                report_status="completed",
                overall_score=score,
                confidence_score=0.9,
                word_count=100 + i * 20,
                speaking_duration_seconds=60.0,
                report_payload={
                    "metadata": {"display_name": "Bob Progress", "speaker_label": "speaker_bob"},
                    "overall_performance": {"overall_score": score},
                    "grammar_analysis": {
                        "score": score + 2,
                        "issues": [
                            {"rule_type": "subject_verb_agreement"},
                            {"rule_type": "preposition_usage"},
                        ],
                    },
                    "vocabulary_analysis": {"score": score},
                    "fluency_analysis": {"score": score - 2},
                    "pronunciation_analysis": {"score": score + 1, "mispronounced_words": []},
                    "ielts_estimate": {"overall_band_estimate": 6.5 + (i * 0.5)},
                    "speaking_metrics": {"total_words": 100 + i * 20},
                },
                generated_at=base_time + timedelta(days=i * 3),
            )
            db.add(snapshot)

        await db.commit()

    # Query historical trajectory
    res = await async_client.get(
        f"/api/v1/reports/participants/{participant_id}/history",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["participant_id"] == participant_id
    assert data["speaker_name"] == "Bob Progress"
    assert data["total_meetings"] == 3
    assert len(data["history_points"]) == 3

    # Trajectory should be 'improving' with delta = 84.0 - 72.0 = +12.0
    trends = data["trends"]
    assert trends["status"] == "active"
    assert trends["trajectory"] == "improving"
    assert trends["overall_delta"] == 12.0

    # Recurring mistakes should contain subject_verb_agreement and preposition_usage
    recurring = [m["rule_type"] for m in data["recurring_mistakes"]]
    assert "subject_verb_agreement" in recurring
    assert "preposition_usage" in recurring
