"""
FluentMeet AI - Step 08 Unit Tests: Scoring Engine & Dynamic Normalization
"""

import pytest
from app.analysis.scoring.engine import ScoringEngine


class TestScoringEngine:
    def test_composite_score_all_categories_available(self):
        engine = ScoringEngine()
        raw_cats = {
            "grammar": {"score": 80.0, "status": "available", "evidence_count": 2},
            "vocabulary": {"score": 90.0, "status": "available", "evidence_count": 3},
            "fluency": {"score": 85.0, "status": "available", "evidence_count": 4},
            "sentence_structure": {"score": 75.0, "status": "available", "evidence_count": 1},
            "communication": {"score": 95.0, "status": "available", "evidence_count": 2},
            "contextual_language": {"score": 90.0, "status": "available", "evidence_count": 5},
        }

        # Expected:
        # 0.25*80 + 0.20*90 + 0.20*85 + 0.10*75 + 0.15*95 + 0.10*90
        # = 20 + 18 + 17 + 7.5 + 14.25 + 9.0 = 85.75 -> 85.8
        summary = engine.evaluate(total_words=120, duration_seconds=45.0, raw_category_results=raw_cats)

        assert summary.score_status == "available"
        assert summary.overall_score == 85.8
        assert summary.evidence_coverage == 1.0
        assert len(summary.category_scores) == 6

    def test_dynamic_denominator_normalization_for_missing_categories(self):
        engine = ScoringEngine()
        # Grammar and Vocabulary available, others unavailable
        raw_cats = {
            "grammar": {"score": 80.0, "status": "available", "evidence_count": 2},
            "vocabulary": {"score": 90.0, "status": "available", "evidence_count": 3},
            "fluency": {"score": None, "status": "unavailable", "evidence_count": 0},
            "sentence_structure": {"score": None, "status": "unavailable", "evidence_count": 0},
            "communication": {"score": None, "status": "unavailable", "evidence_count": 0},
            "contextual_language": {"score": None, "status": "unavailable", "evidence_count": 0},
        }

        # Available weights: grammar (0.25) + vocabulary (0.20) = 0.45
        # Weighted sum: 0.25*80 + 0.20*90 = 20 + 18 = 38
        # Normalized: 38 / 0.45 = 84.44 -> 84.4
        summary = engine.evaluate(total_words=80, duration_seconds=30.0, raw_category_results=raw_cats)

        assert summary.score_status == "available"
        assert summary.overall_score == 84.4
        # Unavailable categories must retain unavailable status and not be 0.0
        fluency_cat = next(c for c in summary.category_scores if c.category == "fluency")
        assert fluency_cat.status == "unavailable"
        assert fluency_cat.score is None

    def test_insufficient_data_rejection_low_word_count(self):
        engine = ScoringEngine()
        raw_cats = {
            "grammar": {"score": 100.0, "status": "available", "evidence_count": 0},
        }

        # Only 20 words (below 50 threshold)
        summary = engine.evaluate(total_words=20, duration_seconds=25.0, raw_category_results=raw_cats)

        assert summary.score_status == "insufficient_data"
        assert summary.overall_score is None
        for cat in summary.category_scores:
            assert cat.status == "insufficient_data"
            assert cat.score is None

    def test_insufficient_data_rejection_low_duration(self):
        engine = ScoringEngine()
        # 60 words but spoke for only 8 seconds (below 15s threshold)
        summary = engine.evaluate(total_words=60, duration_seconds=8.0, raw_category_results={})

        assert summary.score_status == "insufficient_data"
        assert summary.overall_score is None

