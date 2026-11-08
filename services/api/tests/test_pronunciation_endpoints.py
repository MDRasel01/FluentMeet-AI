"""
FluentMeet AI - Step 09 Test Suite: Pronunciation REST Endpoints
Specification: Step 09 - Section 20
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.models.pronunciation import (
    PronunciationAssessment,
    PronunciationWordResult,
    PronunciationPhonemeResult,
    PronunciationProsodyResult,
    PronunciationRecommendation,
    IELTSSpeakingPracticeAssessment,
)
from app.database.session import AsyncSessionLocal


class TestPronunciationEndpoints:
    @pytest.mark.asyncio
    async def test_trigger_and_get_meeting_pronunciation(self, async_client: AsyncClient, auth_token: dict):
        headers = auth_token["headers"]
        user_id = auth_token["user_id"]

        # Create meeting
        m_resp = await async_client.post(
            "/api/v1/meetings",
            json={"title": "Pronunciation API Test Meeting", "platform": "google_meet"},
            headers=headers,
        )
        assert m_resp.status_code == 201
        meeting_id = m_resp.json()["data"]["id"]

        import uuid
        from datetime import datetime, timezone

        # Mock orchestrator run_assessment to simulate successful analysis
        fake_assessment = PronunciationAssessment(
            id=str(uuid.uuid4()),
            meeting_id=meeting_id,
            speaker_label="speaker_user_me",
            assessment_status="completed",
            audio_quality_status="suitable",
            overall_pronunciation_score=82.5,
            evidence_confidence=0.92,
            evidence_coverage=1.0,
            evaluated_word_count=12,
            excluded_word_count=1,
            scoring_version="1.0",
            processing_started_at=datetime.now(timezone.utc),
        )

        with patch("app.api.v1.pronunciation.PronunciationOrchestrator.run_assessment", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = [fake_assessment]

            # 1. Trigger via meeting endpoint
            trig_resp = await async_client.post(
                f"/api/v1/meetings/{meeting_id}/pronunciation",
                json={"force_reassess": True},
                headers=headers,
            )
            assert trig_resp.status_code == 200
            data = trig_resp.json()["data"]
            assert len(data) == 1
            assert data[0]["overall_pronunciation_score"] == 82.5
            assert data[0]["assessment_status"] == "completed"

            # 2. Trigger via body endpoint
            body_resp = await async_client.post(
                "/api/v1/pronunciation/assessments",
                json={"meeting_id": meeting_id, "force_reassess": True},
                headers=headers,
            )
            assert body_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_assessment_subresources(self, async_client: AsyncClient, auth_token: dict):
        """Tests fetching words, prosody, recommendations, and IELTS estimate subresources."""
        headers = auth_token["headers"]
        user_id = auth_token["user_id"]

        m_resp = await async_client.post(
            "/api/v1/meetings",
            json={"title": "Subresources Meeting", "platform": "google_meet"},
            headers=headers,
        )
        meeting_id = m_resp.json()["data"]["id"]

        # Persist dummy assessment and child records directly in DB
        async with AsyncSessionLocal() as session:
            asmt = PronunciationAssessment(
                meeting_id=meeting_id,
                speaker_label="speaker_001",
                assessment_status="completed",
                audio_quality_status="suitable",
                overall_pronunciation_score=86.0,
                evidence_confidence=0.95,
                evaluated_word_count=8,
            )
            session.add(asmt)
            await session.flush()

            # Word and phoneme
            word = PronunciationWordResult(
                assessment_id=asmt.id,
                word_text="think",
                start_time_ms=1000,
                end_time_ms=1400,
                duration_ms=400,
                expected_phonemes="TH IH NG K",
                observed_phonetic_evidence="TH IH NG K",
                pronunciation_score=90.0,
                confidence=0.95,
                evaluation_status="evaluated",
            )
            session.add(word)
            await session.flush()

            session.add(
                PronunciationPhonemeResult(
                    word_result_id=word.id,
                    phoneme_reference="TH",
                    phoneme_score=95.0,
                    issue_type="correct",
                )
            )

            # Prosody
            session.add(
                PronunciationProsodyResult(
                    assessment_id=asmt.id,
                    word_stress_score=88.0,
                    sentence_stress_score=84.0,
                    intonation_score=86.0,
                    speaking_pace_score=85.0,
                    intelligibility_score=92.0,
                    pitch_features={"mean_f0_hz": 145.0, "contour_type": "rising"},
                )
            )

            # Recommendation
            session.add(
                PronunciationRecommendation(
                    assessment_id=asmt.id,
                    category="minimal_pair",
                    title="Voiceless Dental Fricative Practice",
                    description="Practice /θ/ with gentle friction airflow.",
                    suggested_exercise="think / sink",
                    priority="medium",
                    difficulty_level="intermediate",
                )
            )

            # IELTS practice estimate
            session.add(
                IELTSSpeakingPracticeAssessment(
                    assessment_id=asmt.id,
                    fluency_coherence_estimate=7.0,
                    lexical_resource_estimate=7.0,
                    grammatical_accuracy_estimate=7.5,
                    pronunciation_estimate=7.5,
                    overall_practice_estimate=7.5,
                    qualitative_band_descriptor="Good Professional Communicator (Band 7.5 Practice Level)",
                    rubric_version="1.0-qualitative-calibrated",
                    disclaimer_version="1.0",
                    disclaimer_text="Educational practice estimate only. Not an official IELTS score.",
                )
            )
            await session.commit()
            asmt_id = asmt.id

        # 1. GET /pronunciation/assessments/{asmt_id}
        resp = await async_client.get(f"/api/v1/pronunciation/assessments/{asmt_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["overall_pronunciation_score"] == 86.0

        # 2. GET /pronunciation/assessments/{asmt_id}/words
        w_resp = await async_client.get(f"/api/v1/pronunciation/assessments/{asmt_id}/words", headers=headers)
        assert w_resp.status_code == 200
        words_data = w_resp.json()["data"]
        assert len(words_data) == 1
        assert words_data[0]["word_text"] == "think"
        assert len(words_data[0]["phonemes"]) == 1

        # 3. GET /pronunciation/assessments/{asmt_id}/prosody
        p_resp = await async_client.get(f"/api/v1/pronunciation/assessments/{asmt_id}/prosody", headers=headers)
        assert p_resp.status_code == 200
        assert p_resp.json()["data"]["intonation_score"] == 86.0
        assert p_resp.json()["data"]["pitch_features"]["contour_type"] == "rising"

        # 4. GET /pronunciation/assessments/{asmt_id}/recommendations
        r_resp = await async_client.get(f"/api/v1/pronunciation/assessments/{asmt_id}/recommendations", headers=headers)
        assert r_resp.status_code == 200
        assert len(r_resp.json()["data"]) == 1
        assert "Dental Fricative" in r_resp.json()["data"][0]["title"]

        # 5. GET /pronunciation/assessments/{asmt_id}/ielts
        i_resp = await async_client.get(f"/api/v1/pronunciation/assessments/{asmt_id}/ielts", headers=headers)
        assert i_resp.status_code == 200
        assert i_resp.json()["data"]["overall_practice_estimate"] == 7.5
        assert "Band 7.5 Practice Level" in i_resp.json()["data"]["qualitative_band_descriptor"]
        assert "Educational practice estimate only" in i_resp.json()["data"]["disclaimer_text"]
