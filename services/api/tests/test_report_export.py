"""
FluentMeet AI - Step 10 Integration Tests: Report Export Service
Tests CSV sanitization against formula injection and HTML export disclaimer rendering.
"""

import pytest
from httpx import AsyncClient
import app.database.session as app_session_mod
from app.models.base import Meeting
from app.models.report import ReportSnapshot, ReportExport
from app.reports.export import sanitize_csv_cell, MANDATORY_IELTS_DISCLAIMER
from datetime import datetime, timezone


def test_sanitize_csv_cell():
    """Unit test verifying CSV injection defense for dangerous prefixes =, +, -, @."""
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-5+2") == "'-5+2"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_cell("Normal text") == "Normal text"
    assert sanitize_csv_cell(85.5) == "85.5"
    assert sanitize_csv_cell(None) == ""


@pytest.mark.asyncio
async def test_report_export_csv_and_html(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    user_id = auth_token["user_id"]

    # Seed meeting and snapshot with a formula-like string in grammar explanation
    async with app_session_mod.AsyncSessionLocal() as db:
        m = Meeting(
            title="Formula Test Meeting",
            platform="google_meet",
            user_id=user_id,
        )
        db.add(m)
        await db.flush()

        snapshot = ReportSnapshot(
            meeting_id=m.id,
            report_type="individual_participant",
            speaker_label="speaker_danger",
            report_version=1,
            report_status="completed",
            overall_score=80.0,
            confidence_score=0.9,
            word_count=50,
            speaking_duration_seconds=30.0,
            report_payload={
                "metadata": {"display_name": "=HostUser", "speaker_label": "speaker_danger"},
                "overall_performance": {"overall_score": 80.0, "status_label": "Calibrated"},
                "speaking_metrics": {"total_words": 50, "speaking_duration_seconds": 30.0, "words_per_minute": 100.0},
                "grammar_analysis": {
                    "issues": [
                        {
                            "rule_type": "=DANGEROUS_FORMULA",
                            "severity": "high",
                            "offending_text": "+bad text",
                            "corrected_text": "@good text",
                            "explanation": "-calculation result",
                        }
                    ]
                },
                "pronunciation_analysis": {"mispronounced_words": []},
                "recommendations": [],
                "ielts_estimate": {
                    "overall_band_estimate": 7.0,
                    "cefr_level": "B2",
                },
            },
            generated_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)
        await db.commit()
        rep_id = snapshot.id

    # 1. Export CSV
    csv_resp = await async_client.post(
        f"/api/v1/reports/{rep_id}/export/csv",
        headers=headers,
    )
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    csv_text = csv_resp.text

    # Verify formula prefixes were properly neutralized with prepended single quote (')
    assert "'=HostUser" in csv_text
    assert "'=DANGEROUS_FORMULA" in csv_text
    assert "'+bad text" in csv_text
    assert "'@good text" in csv_text
    assert "'-calculation result" in csv_text

    # 2. Export HTML
    html_resp = await async_client.post(
        f"/api/v1/reports/{rep_id}/export/html",
        headers=headers,
    )
    assert html_resp.status_code == 200
    assert "text/html" in html_resp.headers["content-type"]
    html_text = html_resp.text

    # Verify mandatory educational IELTS disclaimer is present
    assert MANDATORY_IELTS_DISCLAIMER in html_text
    assert "FluentMeet AI" in html_text
