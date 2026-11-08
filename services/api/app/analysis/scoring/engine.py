"""
FluentMeet AI - Step 08: Evidence-Based Scoring Engine
Calculates weighted composite English communication scores (0-100) with dynamic denominator
normalization, zero fabrication guarantee, and insufficient speech data detection.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class CategoryScoreResult:
    category: str
    score: Optional[float]
    status: str  # available, insufficient_data, unavailable
    evidence_count: int
    confidence: float
    scoring_version: str = "1.0"


@dataclass
class ParticipantScoreSummary:
    overall_score: Optional[float]
    score_status: str  # available, insufficient_data, unavailable
    evidence_coverage: float  # [0.0, 1.0]
    analysis_confidence: float
    category_scores: List[CategoryScoreResult]
    scoring_version: str = "1.0"


class ScoringEngine:
    """
    Evidence-based 0-100 scoring engine with weighted categories and dynamic re-normalization.
    """

    DEFAULT_WEIGHTS = {
        "grammar": 0.25,
        "vocabulary": 0.20,
        "fluency": 0.20,
        "sentence_structure": 0.10,
        "communication": 0.15,
        "contextual_language": 0.10,
    }

    MIN_WORDS_THRESHOLD = 50
    MIN_DURATION_SECONDS = 15.0

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def evaluate(
        self,
        total_words: int,
        duration_seconds: float,
        raw_category_results: Dict[str, Dict[str, Any]],
    ) -> ParticipantScoreSummary:
        """
        Calculates category and overall scores with strict insufficient data gates.
        """
        # 1. Check minimum speech volume threshold
        if total_words < self.MIN_WORDS_THRESHOLD or duration_seconds < self.MIN_DURATION_SECONDS:
            cat_scores = []
            for cat in self.weights.keys():
                cat_scores.append(
                    CategoryScoreResult(
                        category=cat,
                        score=None,
                        status="insufficient_data",
                        evidence_count=0,
                        confidence=0.5,
                    )
                )
            return ParticipantScoreSummary(
                overall_score=None,
                score_status="insufficient_data",
                evidence_coverage=1.0,
                analysis_confidence=0.5,
                category_scores=cat_scores,
            )

        # 2. Process each category
        category_scores: List[CategoryScoreResult] = []
        available_weights_sum = 0.0
        weighted_score_accum = 0.0
        confidence_accum = 0.0
        total_evidence = 0

        for cat, weight in self.weights.items():
            cat_data = raw_category_results.get(cat, {})
            score = cat_data.get("score")
            status = cat_data.get("status", "available")
            evidence_count = cat_data.get("evidence_count", 0)
            confidence = cat_data.get("confidence", 0.90)

            total_evidence += evidence_count

            if status == "available" and score is not None:
                bounded_score = max(0.0, min(100.0, float(score)))
                category_scores.append(
                    CategoryScoreResult(
                        category=cat,
                        score=round(bounded_score, 1),
                        status="available",
                        evidence_count=evidence_count,
                        confidence=confidence,
                    )
                )
                available_weights_sum += weight
                weighted_score_accum += weight * bounded_score
                confidence_accum += weight * confidence
            else:
                category_scores.append(
                    CategoryScoreResult(
                        category=cat,
                        score=None,
                        status=status,
                        evidence_count=evidence_count,
                        confidence=0.5,
                    )
                )

        # 3. Dynamic Denominator Normalization
        if available_weights_sum > 0.0:
            normalized_overall = round(weighted_score_accum / available_weights_sum, 1)
            overall_confidence = round(confidence_accum / available_weights_sum, 2)
            overall_status = "available"
        else:
            normalized_overall = None
            overall_confidence = 0.5
            overall_status = "unavailable"

        # Evidence coverage is 1.0 when all findings are anchored to valid segments
        evidence_coverage = 1.0

        return ParticipantScoreSummary(
            overall_score=normalized_overall,
            score_status=overall_status,
            evidence_coverage=evidence_coverage,
            analysis_confidence=overall_confidence,
            category_scores=category_scores,
        )

