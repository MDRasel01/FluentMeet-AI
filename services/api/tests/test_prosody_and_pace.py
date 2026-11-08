"""
FluentMeet AI - Step 09 Test Suite: Prosody, Intonation, Speaking Pace & Intelligibility
Specification: Step 09 - Section 10, 11, 12, 13
"""

import pytest
import numpy as np
from app.pronunciation.acoustic.prosody import ProsodyAnalysisEngine, ProsodyReport
from app.pronunciation.acoustic.pace import SpeakingPaceAnalyzer, SpeakingPaceReport
from app.pronunciation.acoustic.intelligibility import IntelligibilityAnalyzer, IntelligibilityReport


class TestProsodyAndIntonation:
    def test_f0_pitch_contour_extraction(self):
        """Autocorrelation correctly estimates pitch contour of periodic signal."""
        engine = ProsodyAnalysisEngine()
        sample_rate = 16000
        # 1.0 second of 150 Hz tone (male/neutral speaking register)
        t = np.linspace(0, 1.0, sample_rate, False)
        sine_150 = 0.6 * np.sin(2 * np.pi * 150 * t)
        samples = sine_150.astype(np.float32)

        pitch_features = engine.extract_f0_contour(samples, sample_rate=sample_rate)

        assert 140.0 <= pitch_features.mean_f0_hz <= 160.0
        assert pitch_features.contour_type in ("level", "rising", "falling", "complex")

    def test_analyze_prosody_scoring(self):
        engine = ProsodyAnalysisEngine()
        sample_rate = 16000
        t = np.linspace(0, 2.0, sample_rate * 2, False)
        # Moderate pitch modulation from 140 to 180 Hz
        modulated = 0.5 * np.sin(2 * np.pi * (140 + 40 * t / 2.0) * t)
        pcm_bytes = (modulated * 16384).astype(np.int16).tobytes()

        report: ProsodyReport = engine.analyze_prosody(pcm_bytes, words_count=10, sample_rate=sample_rate)

        assert report.word_stress_score >= 60.0
        assert report.sentence_stress_score >= 60.0
        assert report.intonation_score >= 60.0
        assert report.pitch_features.mean_f0_hz > 100.0


class TestSpeakingPaceAnalyzer:
    def test_speaking_pace_and_pause_taxonomy(self):
        analyzer = SpeakingPaceAnalyzer()

        # 10 words spoken across 4 seconds = 150 WPM (optimal business tempo)
        timestamps = [
            {"start_ms": 0, "end_ms": 250},
            {"start_ms": 300, "end_ms": 550},
            {"start_ms": 600, "end_ms": 900},
            {"start_ms": 950, "end_ms": 1200},
            {"start_ms": 1300, "end_ms": 1600},
            {"start_ms": 2000, "end_ms": 2300},  # 400ms pause between 1600 and 2000 (normal pause)
            {"start_ms": 2350, "end_ms": 2600},
            {"start_ms": 2650, "end_ms": 2900},
            {"start_ms": 3000, "end_ms": 3300},
            {"start_ms": 3400, "end_ms": 3800},
        ]

        report: SpeakingPaceReport = analyzer.analyze_pace(
            word_timestamps=timestamps,
            total_duration_ms=4000,
        )

        assert 140.0 <= report.wpm <= 165.0
        assert report.pace_consistency in ("steady", "variable")
        assert report.speaking_pace_score >= 80.0
        assert len(report.pauses) >= 1
        assert any(p.pause_type == "normal_pause" for p in report.pauses)

    def test_speaking_pace_rushed_delivery(self):
        analyzer = SpeakingPaceAnalyzer()
        # 10 words crammed into 2 seconds = 300 WPM
        timestamps = [{"start_ms": i * 200, "end_ms": i * 200 + 180} for i in range(10)]
        report = analyzer.analyze_pace(timestamps, total_duration_ms=2000)

        assert report.wpm > 200.0
        assert report.pace_consistency == "rushed"
        assert report.speaking_pace_score < 75.0


class TestIntelligibilityAnalyzer:
    def test_accent_neutrality_intelligibility(self):
        """Intelligibility reflects listener comprehension without penalizing accent conformity."""
        analyzer = IntelligibilityAnalyzer()

        report: IntelligibilityReport = analyzer.analyze_intelligibility(
            avg_phoneme_score=85.0,
            avg_word_confidence=0.92,
            snr_db=24.0,
            clipping_ratio=0.001,
            evaluated_words_count=25,
        )

        assert report.intelligibility_score >= 85.0
        assert report.classification == "High intelligibility"
        assert "effortless" in report.summary.lower()

    def test_intelligibility_insufficient_speech(self):
        analyzer = IntelligibilityAnalyzer()
        report = analyzer.analyze_intelligibility(
            avg_phoneme_score=80.0,
            avg_word_confidence=0.8,
            snr_db=15.0,
            clipping_ratio=0.0,
            evaluated_words_count=3,  # < 5 words
        )
        assert report.classification == "Insufficient evidence"
        assert report.intelligibility_score == 0.0

