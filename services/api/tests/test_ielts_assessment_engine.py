"""
FluentMeet AI - Step 09 Test Suite: IELTS-Style Speaking Practice Assessment & Recommendations
Specification: Step 09 - Section 14, 15
"""

import pytest
from app.pronunciation.scoring.ielts_engine import IELTSAssessmentEngine, IELTSEstimateResult
from app.pronunciation.feedback.recommendation_generator import (
    PronunciationRecommendationGenerator,
    PronunciationExercise,
)
from app.pronunciation.acoustic.phonetics import WordPronunciationEvidence, PhonemeObservation
from app.pronunciation.acoustic.prosody import ProsodyReport, PitchFeatures
from app.pronunciation.acoustic.pace import SpeakingPaceReport


class TestIELTSAssessmentEngine:
    def test_score_to_band_mapping(self):
        engine = IELTSAssessmentEngine()
        assert engine.score_to_band(95.0) == 9.0
        assert engine.score_to_band(85.0) == 8.0
        assert engine.score_to_band(76.0) == 7.0
        assert engine.score_to_band(68.0) == 6.5
        assert engine.score_to_band(50.0) == 5.0
        assert engine.score_to_band(None) == 5.5

    def test_ielts_practice_estimate_4_dimensions_and_rounding(self):
        """Calculates 4 dimensions, rounds to nearest 0.5, and attaches educational disclaimer."""
        engine = IELTSAssessmentEngine()

        result: IELTSEstimateResult = engine.generate_assessment(
            pronunciation_score=78.0,  # ~7.0 band
            fluency_score=75.0,        # ~7.0 band
            vocabulary_score=70.0,     # ~6.5 band
            grammar_score=80.0,        # ~7.5 band
            confidence=0.92,
        )

        assert result.assessment_status == "completed"
        assert result.pronunciation_estimate == 7.0
        assert result.fluency_coherence_estimate == 7.0
        assert result.lexical_resource_estimate == 6.5
        assert result.grammatical_accuracy_estimate == 7.5
        # Average: (7.0 + 7.0 + 6.5 + 7.5) / 4 = 7.0
        assert result.overall_practice_estimate == 7.0
        assert "Band 7.0 Practice Level" in result.qualitative_band_descriptor
        assert "Educational practice estimate only" in result.disclaimer_text

    def test_ielts_insufficient_evidence_when_pronunciation_missing(self):
        """If acoustic pronunciation score is None, returns status insufficient_evidence and overall None."""
        engine = IELTSAssessmentEngine()
        result = engine.generate_assessment(
            pronunciation_score=None,
            fluency_score=80.0,
            vocabulary_score=80.0,
            grammar_score=80.0,
        )

        assert result.assessment_status == "insufficient_evidence"
        assert result.overall_practice_estimate is None
        assert "Insufficient" in result.qualitative_band_descriptor


class TestPronunciationRecommendations:
    def test_minimal_pairs_generated_for_th_substitution(self):
        generator = PronunciationRecommendationGenerator()

        word_evidences = [
            WordPronunciationEvidence(
                word_text="think",
                start_time_ms=1000,
                end_time_ms=1300,
                duration_ms=300,
                audio_segment_reference="test.pcm",
                expected_phonemes="TH IH NG K",
                observed_phonemes="T IH NG K",
                pronunciation_score=60.0,
                confidence=0.90,
                evaluation_status="evaluated",
                exclusion_reason=None,
                phonemes=[
                    PhonemeObservation(
                        phoneme_reference="TH",
                        phoneme_evidence="T",
                        phoneme_score=50.0,
                        confidence=0.90,
                        issue_type="substitution",
                    )
                ],
            ),
            WordPronunciationEvidence(
                word_text="three",
                start_time_ms=1400,
                end_time_ms=1700,
                duration_ms=300,
                audio_segment_reference="test.pcm",
                expected_phonemes="TH R IY",
                observed_phonemes="T R IY",
                pronunciation_score=60.0,
                confidence=0.90,
                evaluation_status="evaluated",
                exclusion_reason=None,
                phonemes=[
                    PhonemeObservation(
                        phoneme_reference="TH",
                        phoneme_evidence="T",
                        phoneme_score=50.0,
                        confidence=0.90,
                        issue_type="substitution",
                    )
                ],
            ),
        ]

        dummy_prosody = ProsodyReport(
            word_stress_score=85.0,
            sentence_stress_score=85.0,
            intonation_score=80.0,
            pitch_features=PitchFeatures(140.0, 110.0, 180.0, 70.0, "rising", []),
            syllable_analysis={},
            confidence=0.90,
        )
        dummy_pace = SpeakingPaceReport(
            wpm=145.0,
            syllables_per_minute=210.0,
            active_speaking_ms=3000,
            total_pause_ms=500,
            speech_to_pause_ratio=6.0,
            pace_consistency="steady",
            speaking_pace_score=88.0,
            pause_metrics={},
            pauses=[],
        )

        exercises: list[PronunciationExercise] = generator.generate_recommendations(
            word_evidences=word_evidences,
            prosody=dummy_prosody,
            pace=dummy_pace,
        )

        assert len(exercises) >= 1
        th_ex = next((e for e in exercises if e.category == "minimal_pair"), None)
        assert th_ex is not None
        assert "Dental Fricative" in th_ex.title
        assert "think / sink" in th_ex.suggested_exercise or "three / tree" in th_ex.suggested_exercise

