"""
FluentMeet AI - Step 09: Pronunciation Scoring Engine
Specification: Step 09 - Section 9 & Section 18
Calculates deterministic pronunciation scores, evidence coverage, and confidence levels.
Prevents score fabrication on insufficient or corrupted acoustic evidence.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.pronunciation.acoustic.phonetics import WordPronunciationEvidence
from app.pronunciation.acoustic.prosody import ProsodyReport
from app.pronunciation.acoustic.pace import SpeakingPaceReport
from app.pronunciation.acoustic.intelligibility import IntelligibilityReport


@dataclass
class PronunciationScoreResult:
    overall_score: Optional[float]  # 0.0 - 100.0 or None
    assessment_status: str  # completed, partial, insufficient_evidence
    evidence_confidence: float  # [0.0, 1.0]
    evidence_coverage: float  # [0.0, 1.0]
    evaluated_word_count: int
    excluded_word_count: int
    word_accuracy_score: Optional[float]
    phoneme_fidelity_score: Optional[float]
    scoring_version: str = "1.0"
    explanation: str = ""


class PronunciationScorer:
    """
    Computes calibrated pronunciation scores based on acoustic word and phoneme observations.
    """

    MIN_EVALUATED_WORDS = 5

    def calculate_scores(
        self,
        word_evidences: List[WordPronunciationEvidence],
        prosody: ProsodyReport,
        pace: SpeakingPaceReport,
        intelligibility: IntelligibilityReport,
    ) -> PronunciationScoreResult:
        """
        Synthesizes word acoustic scores, phoneme observations, stress, and intonation.
        """
        evaluated_words = [w for w in word_evidences if w.evaluation_status == "evaluated"]
        excluded_words = [w for w in word_evidences if w.evaluation_status in ("excluded", "uncertain")]

        evaluated_count = len(evaluated_words)
        excluded_count = len(excluded_words)
        total_count = evaluated_count + excluded_count

        # 1. Insufficient Evidence Gate
        if evaluated_count < self.MIN_EVALUATED_WORDS:
            return PronunciationScoreResult(
                overall_score=None,
                assessment_status="insufficient_evidence",
                evidence_confidence=0.5,
                evidence_coverage=round(evaluated_count / max(1, total_count), 2),
                evaluated_word_count=evaluated_count,
                excluded_word_count=excluded_count,
                word_accuracy_score=None,
                phoneme_fidelity_score=None,
                scoring_version="1.0",
                explanation=f"Evaluated only {evaluated_count} words (minimum {self.MIN_EVALUATED_WORDS} required for acoustic validity).",
            )

        # 2. Word Pronunciation Accuracy (45% weight)
        word_scores = [w.pronunciation_score for w in evaluated_words]
        avg_word_score = float(sum(word_scores) / max(1, len(word_scores)))

        # 3. Phoneme Fidelity (25% weight)
        all_phonemes = [p for w in evaluated_words for p in w.phonemes if p.evaluation_status == "evaluated"]
        if all_phonemes:
            avg_phoneme_score = float(sum(p.phoneme_score for p in all_phonemes) / max(1, len(all_phonemes)))
        else:
            avg_phoneme_score = avg_word_score

        # 4. Stress and Intonation (15% + 15% weight)
        stress_score = prosody.word_stress_score
        intonation_score = prosody.intonation_score

        # Composite Pronunciation Score (0 - 100)
        overall = (
            0.45 * avg_word_score
            + 0.25 * avg_phoneme_score
            + 0.15 * stress_score
            + 0.15 * intonation_score
        )
        overall_bounded = round(max(0.0, min(100.0, overall)), 1)

        # Evidence Coverage
        coverage = round(evaluated_count / max(1, total_count), 2)

        # Confidence: average of word acoustic confidence and prosody confidence
        avg_word_conf = sum(w.confidence for w in evaluated_words) / max(1, evaluated_count)
        composite_conf = round(0.70 * avg_word_conf + 0.30 * prosody.confidence, 2)

        return PronunciationScoreResult(
            overall_score=overall_bounded,
            assessment_status="completed",
            evidence_confidence=composite_conf,
            evidence_coverage=coverage,
            evaluated_word_count=evaluated_count,
            excluded_word_count=excluded_count,
            word_accuracy_score=round(avg_word_score, 1),
            phoneme_fidelity_score=round(avg_phoneme_score, 1),
            scoring_version="1.0",
            explanation=f"Successfully evaluated {evaluated_count} words with {coverage*100:.0f}% evidence coverage.",
        )

