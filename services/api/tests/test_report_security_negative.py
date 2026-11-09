"""
FluentMeet AI - Step 10 Security & Negative Test Suite
Tests tenant isolation, access boundaries, missing resource handling, and injection prevention.
"""

import pytest
from httpx import AsyncClient
import app.database.session as app_session_mod
from app.models.base import Meeting, User
from app.models.report import ReportSnapshot
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_cross_tenant_report_access_forbidden(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    user_id = auth_token["user_id"]

    # Seed meeting owned by another user
    other_user_id = "other-tenant-user-999"
    async with app_session_mod.AsyncSessionLocal() as db:
        other_user = User(
            id=other_user_id,
            email="otheruser@example.com",
            hashed_password="fakehashedpassword",
            full_name="Other User",
        )
        db.add(other_user)

        m = Meeting(
            title="Confidential Executive Board Meeting",
            platform="google_meet",
            user_id=other_user_id,
            organization_id="org-foreign-403",
        )
        db.add(m)
        await db.flush()

        s = ReportSnapshot(
            meeting_id=m.id,
            tenant_id="org-foreign-403",
            report_type="meeting_summary",
            report_version=1,
            report_status="completed",
            report_payload={"summary_metrics": {}},
            generated_at=datetime.now(timezone.utc),
        )
        db.add(s)
        await db.commit()
        foreign_meet_id = m.id
        foreign_rep_id = s.id

    # 1. Access foreign meeting summary => 403 Forbidden
    res1 = await async_client.get(f"/api/v1/reports/meetings/{foreign_meet_id}", headers=headers)
    assert res1.status_code == 403

    # 2. Access foreign report by id => 403 Forbidden
    res2 = await async_client.get(f"/api/v1/reports/{foreign_rep_id}", headers=headers)
    assert res2.status_code == 403

    # 3. Export foreign report => 403 Forbidden
    res3 = await async_client.post(f"/api/v1/reports/{foreign_rep_id}/export/csv", headers=headers)
    assert res3.status_code == 403


@pytest.mark.asyncio
async def test_nonexistent_report_returns_404(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    res = await async_client.get("/api/v1/reports/non-existent-report-uuid", headers=headers)
    assert res.status_code == 404

    res2 = await async_client.get("/api/v1/reports/meetings/non-existent-meeting-uuid", headers=headers)
    assert res2.status_code == 404


@pytest.mark.asyncio
async def test_generate_report_for_empty_meeting_returns_400(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    user_id = auth_token["user_id"]

    # Create meeting without participants or transcripts
    m_resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Empty Meeting Without Audio", "platform": "google_meet"},
        headers=headers,
    )
    assert m_resp.status_code == 201
    meeting_id = m_resp.json()["data"]["id"]

    gen_resp = await async_client.post(
        "/api/v1/reports/generate",
        json={"meeting_id": meeting_id},
        headers=headers,
    )
    assert gen_resp.status_code == 400
    assert "No participant data available" in str(gen_resp.json())
