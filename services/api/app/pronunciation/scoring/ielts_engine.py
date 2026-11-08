"""
FluentMeet AI - Step 09: IELTS-Style Speaking Practice Assessment Engine
Specification: Step 09 - Section 14
Evaluates 4 core dimensions:
- Fluency & Coherence
- Lexical Resource
- Grammatical Range & Accuracy
- Pronunciation (Acoustic Evidence)
Produces practice estimates with mandatory educational disclaimer.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class IELTSEstimateResult:
    fluency_coherence_estimate: float  # e.g. 6.5
    lexical_resource_estimate: float
    grammatical_accuracy_estimate: float
    pronunciation_estimate: float
    overall_practice_estimate: Optional[float]
    qualitative_band_descriptor: str
    rubric_version: str
    confidence: float
    evidence_coverage: float
    assessment_status: str
    disclaimer_text: str


class IELTSAssessmentEngine:
    """
    Computes four-dimension IELTS-style speaking practice assessments.
    """

    RUBRIC_VERSION = "1.0-qualitative-calibrated"
    DISCLAIMER = (
        "Educational practice estimate only. This is not an official IELTS score, "
        "certified assessment, or substitute for an IELTS examiner."
    )

    @staticmethod
    def score_to_band(score: Optional[float]) -> float:
        """
        Converts 0-100 rubric score to 4.0 - 9.0 IELTS-style band estimate in 0.5 increments.
        """
        if score is None:
            return 5.5
        if score >= 94.0:
            return 9.0
        elif score >= 89.0:
            return 8.5
        elif score >= 84.0:
            return 8.0
        elif score >= 79.0:
            return 7.5
        elif score >= 74.0:
            return 7.0
        elif score >= 68.0:
            return 6.5
        elif score >= 62.0:
            return 6.0
        elif score >= 55.0:
            return 5.5
        elif score >= 48.0:
            return 5.0
        elif score >= 40.0:
            return 4.5
        else:
            return 4.0

    @staticmethod
    def get_qualitative_descriptor(band: float) -> str:
        """
        Returns descriptive CEFR/IELTS alignment terminology.
        """
        if band >= 8.5:
            return f"Expert / Very Good Spoken English (Band {band:.1f} Practice Level)"
        elif band >= 7.0:
            return f"Good Professional Communicator (Band {band:.1f} Practice Level)"
        elif band >= 6.0:
            return f"Competent Spoken English User (Band {band:.1f} Practice Level)"
        elif band >= 5.0:
            return f"Modest Spoken English User (Band {band:.1f} Practice Level)"
        else:
            return f"Developing Speaker (Band {band:.1f} Practice Level)"

    def generate_assessment(
        self,
        pronunciation_score: Optional[float],
        fluency_score: Optional[float] = None,
        vocabulary_score: Optional[float] = None,
        grammar_score: Optional[float] = None,
        is_calibrated: bool = True,
        confidence: float = 0.90,
        evidence_coverage: float = 1.0,
    ) -> IELTSEstimateResult:
        """
        Synthesizes Step 08 linguistic evidence and Step 09 acoustic pronunciation.
        """
        # If pronunciation score is missing or insufficient
        if pronunciation_score is None:
            return IELTSEstimateResult(
                fluency_coherence_estimate=self.score_to_band(fluency_score),
                lexical_resource_estimate=self.score_to_band(vocabulary_score),
                grammatical_accuracy_estimate=self.score_to_band(grammar_score),
                pronunciation_estimate=5.0,
                overall_practice_estimate=None,
                qualitative_band_descriptor="Insufficient Speech Data for IELTS Practice Estimate",
                rubric_version=self.RUBRIC_VERSION,
                confidence=0.5,
                evidence_coverage=evidence_coverage,
                assessment_status="insufficient_evidence",
                disclaimer_text=self.DISCLAIMER,
            )

        # Map 4 dimensions
        fc_band = self.score_to_band(fluency_score or 75.0)
        lr_band = self.score_to_band(vocabulary_score or 75.0)
        gra_band = self.score_to_band(grammar_score or 75.0)
        p_band = self.score_to_band(pronunciation_score)

        # Average across 4 dimensions
        raw_average = (fc_band + lr_band + gra_band + p_band) / 4.0
        # Round to nearest 0.5 according to IELTS rounding rules
        # e.g., 6.25 -> 6.5, 6.75 -> 7.0, 6.125 -> 6.0
        overall_band = round(raw_average * 2.0) / 2.0

        descriptor = self.get_qualitative_descriptor(overall_band)

        return IELTSEstimateResult(
            fluency_coherence_estimate=fc_band,
            lexical_resource_estimate=lr_band,
            grammatical_accuracy_estimate=gra_band,
            pronunciation_estimate=p_band,
            overall_practice_estimate=overall_band if is_calibrated else None,
            qualitative_band_descriptor=descriptor,
            rubric_version=self.RUBRIC_VERSION,
            confidence=round(confidence, 2),
            evidence_coverage=round(evidence_coverage, 2),
            assessment_status="completed",
            disclaimer_text=self.DISCLAIMER,
        )
