"""
FluentMeet AI - Step 10 Integration Tests: Dashboard Analytics Endpoints
Tests summary cards, historical trends, and recent meeting feeds.
"""

import pytest
from httpx import AsyncClient
import app.database.session as app_session_mod
from app.models.base import Meeting
from app.models.report import ReportSnapshot
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_dashboard_analytics_endpoints(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    user_id = auth_token["user_id"]

    # Seed meeting and snapshots
    async with app_session_mod.AsyncSessionLocal() as db:
        m1 = Meeting(
            title="Sprint Retro",
            platform="google_meet",
            user_id=user_id,
        )
        db.add(m1)
        await db.flush()

        # Add participant report snapshot
        now = datetime.now(timezone.utc)
        s1 = ReportSnapshot(
            meeting_id=m1.id,
            report_type="individual_participant",
            speaker_label="speaker_1",
            report_version=1,
            report_status="completed",
            overall_score=82.0,
            confidence_score=0.9,
            word_count=50,
            speaking_duration_seconds=30.0,
            report_payload={
                "grammar_analysis": {"issues": [{"rule_type": "subject_verb_agreement"}]},
                "ielts_estimate": {"overall_band_estimate": 7.0},
            },
            generated_at=now,
        )
        db.add(s1)

        # Add summary snapshot
        s_sum = ReportSnapshot(
            meeting_id=m1.id,
            report_type="meeting_summary",
            report_version=1,
            report_status="completed",
            overall_score=82.0,
            word_count=50,
            speaking_duration_seconds=30.0,
            report_payload={"summary_metrics": {"participant_count": 1, "total_duration_seconds": 30.0}},
            generated_at=now,
        )
        db.add(s_sum)
        await db.commit()

    # 1. GET /api/v1/dashboard/summary
    res_sum = await async_client.get("/api/v1/dashboard/summary", headers=headers)
    assert res_sum.status_code == 200
    data_sum = res_sum.json()["data"]
    assert data_sum["total_meetings_analyzed"] >= 1
    assert data_sum["average_english_score"] is not None
    assert data_sum["ielts_average_band"] == 7.0

    # 2. GET /api/v1/dashboard/trends
    res_trends = await async_client.get("/api/v1/dashboard/trends", headers=headers)
    assert res_trends.status_code == 200
    data_trends = res_trends.json()["data"]
    assert len(data_trends["dates"]) >= 1
    assert len(data_trends["overall_scores"]) >= 1

    # 3. GET /api/v1/dashboard/recent-meetings
    res_rec = await async_client.get("/api/v1/dashboard/recent-meetings", headers=headers)
    assert res_rec.status_code == 200
    data_rec = res_rec.json()["data"]
    assert len(data_rec) >= 1
    assert data_rec[0]["title"] is not None
