"""
FluentMeet AI - Step 10 Unit Tests: Report Validation Engine
Tests evidence thresholds, score calibration, and missing category handling.
"""

import pytest
from app.reports.collector import CollectedParticipantData
from app.reports.validator import ReportValidationEngine


class TestReportValidationEngine:
    def test_insufficient_speech_evidence(self):
        """Speech with fewer than 5 words must be flagged insufficient evidence without guessing a score."""
        pdata = CollectedParticipantData(speaker_label="speaker_0")
        pdata.total_words = 3
        pdata.speaking_duration_seconds = 2.0
        pdata.grammar_score = 80.0
        pdata.vocabulary_score = 80.0
        pdata.fluency_score = 80.0
        pdata.pronunciation_score = 80.0

        val = ReportValidationEngine.validate_participant(pdata)
        assert val.is_calibrated is False
        assert val.overall_score is None
        assert val.report_status == "insufficient_evidence"
        assert val.status_label == "Insufficient speech evidence for calibrated score"
        assert "insufficient_speech" in val.missing_components

    def test_missing_category_handling_no_fabrication(self):
        """If a core category (e.g. pronunciation) is missing, never substitute 0; mark Overall score unavailable."""
        pdata = CollectedParticipantData(speaker_label="speaker_1")
        pdata.total_words = 65
        pdata.speaking_duration_seconds = 25.0
        pdata.grammar_score = 85.0
        pdata.vocabulary_score = 78.0
        pdata.fluency_score = 82.0
        pdata.pronunciation_score = None  # Missing!

        val = ReportValidationEngine.validate_participant(pdata)
        assert val.is_calibrated is False
        assert val.overall_score is None
        assert val.status_label == "Overall score unavailable"
        assert val.report_status == "partial"
        assert "pronunciation" in val.missing_components

    def test_calibrated_overall_score_calculation(self):
        """When all 4 core pillars are present, calibrated overall score is weighted 25% each."""
        pdata = CollectedParticipantData(speaker_label="speaker_host")
        pdata.total_words = 120
        pdata.speaking_duration_seconds = 50.0
        pdata.grammar_score = 80.0
        pdata.vocabulary_score = 90.0
        pdata.fluency_score = 70.0
        pdata.pronunciation_score = 84.0
        pdata.step08_confidence = 0.90
        pdata.step09_confidence = 0.92

        val = ReportValidationEngine.validate_participant(pdata)
        assert val.is_calibrated is True
        # 0.25 * (80 + 90 + 70 + 84) = 0.25 * 324 = 81.0
        assert val.overall_score == 81.0
        assert val.status_label == "Calibrated"
        assert val.report_status == "completed"
        assert val.missing_components == []
        assert val.confidence_score == 0.91

