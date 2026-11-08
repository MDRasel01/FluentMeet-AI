"""
FluentMeet AI - Step 09: Speech Clarity & Intelligibility Analyzer
Specification: Step 09 - Section 13
Estimates spoken English intelligibility without penalizing valid non-native or regional accents.
Prioritizes listener comprehension and acoustic stability over accent conformity.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class IntelligibilityReport:
    intelligibility_score: float  # 0.0 - 100.0
    classification: str  # High intelligibility, Generally intelligible, Partially difficult to understand, Insufficient evidence
    clarity_confidence: float
    acoustic_clarity_score: float
    phonemic_clarity_score: float
    summary: str


class IntelligibilityAnalyzer:
    """
    Evaluates how easily a speaker's English can be understood across international business teams.
    """

    def analyze_intelligibility(
        self,
        avg_phoneme_score: float,
        avg_word_confidence: float,
        snr_db: float,
        clipping_ratio: float,
        evaluated_words_count: int,
    ) -> IntelligibilityReport:
        """
        Synthesizes acoustic stability, phonemic contrast clarity, and recognition confidence.
        """
        if evaluated_words_count < 5:
            return IntelligibilityReport(
                intelligibility_score=0.0,
                classification="Insufficient evidence",
                clarity_confidence=0.5,
                acoustic_clarity_score=0.0,
                phonemic_clarity_score=0.0,
                summary="Insufficient spoken evidence to calibrate speech intelligibility.",
            )

        # 1. Acoustic clarity (SNR and clean signal)
        acoustic_clarity = min(100.0, max(50.0, 70.0 + (snr_db * 0.8) - (clipping_ratio * 100.0)))

        # 2. Phonemic clarity (contrast distinctness)
        phonemic_clarity = min(100.0, max(50.0, avg_phoneme_score * 0.9 + avg_word_confidence * 15.0))

        # Composite intelligibility (60% phonemic clarity + 40% acoustic clarity)
        composite = round(0.60 * phonemic_clarity + 0.40 * acoustic_clarity, 1)

        # Categorization based on functional communication standards
        if composite >= 85.0:
            classification = "High intelligibility"
            summary = "Speech is effortless to understand with clear phonetic contrasts and vocal projection."
        elif composite >= 70.0:
            classification = "Generally intelligible"
            summary = "Speech is clearly understood in international business discussions with minor accent variations."
        else:
            classification = "Partially difficult to understand"
            summary = "Occasional sound substitutions or acoustic friction may require repetition in fast-paced meetings."

        confidence = min(0.98, max(0.70, 0.70 + (evaluated_words_count / 100.0) * 0.25))

        return IntelligibilityReport(
            intelligibility_score=composite,
            classification=classification,
            clarity_confidence=round(confidence, 2),
            acoustic_clarity_score=round(acoustic_clarity, 1),
            phonemic_clarity_score=round(phonemic_clarity, 1),
            summary=summary,
        )

