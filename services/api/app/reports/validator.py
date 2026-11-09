"""
FluentMeet AI - Step 10: Report Validation Engine
Enforces strict calibration rules, prevents score fabrication, and validates evidence thresholds.
"""

from typing import Dict, Any, List, Optional, Tuple
from app.reports.collector import CollectedParticipantData


class ValidationResult:
    def __init__(
        self,
        is_calibrated: bool,
        overall_score: Optional[float],
        confidence_score: Optional[float],
        status_label: str,
        report_status: str,
        missing_components: List[str],
        validation_notes: List[str],
    ):
        self.is_calibrated = is_calibrated
        self.overall_score = overall_score
        self.confidence_score = confidence_score
        self.status_label = status_label
        self.report_status = report_status
        self.missing_components = missing_components
        self.validation_notes = validation_notes


class ReportValidationEngine:
    """
    Validates participant inputs according to strict production quality rules.
    """
    MIN_EVALUATED_WORDS = 5
    MIN_DURATION_SECONDS = 3.0

    @classmethod
    def validate_participant(
        cls,
        pdata: CollectedParticipantData,
        scoring_rubric_version: str = "1.0"
    ) -> ValidationResult:
        """
        Validates evidence sufficiency and computes calibrated overall score.
        NEVER fabricates zero for missing metrics.
        """
        notes: List[str] = []
        missing: List[str] = []

        # 1. Evidence sufficiency check
        if pdata.total_words < cls.MIN_EVALUATED_WORDS:
            return ValidationResult(
                is_calibrated=False,
                overall_score=None,
                confidence_score=0.1,
                status_label="Insufficient speech evidence for calibrated score",
                report_status="insufficient_evidence",
                missing_components=["insufficient_speech"],
                validation_notes=[f"Evaluated words ({pdata.total_words}) below minimum threshold ({cls.MIN_EVALUATED_WORDS})"]
            )

        # 2. Check core pillars
        if pdata.grammar_score is None:
            missing.append("grammar")
        if pdata.vocabulary_score is None:
            missing.append("vocabulary")
        if pdata.fluency_score is None:
            missing.append("fluency")
        if pdata.pronunciation_score is None:
            missing.append("pronunciation")

        # 3. Missing categories rule: NEVER fabricate zero!
        if missing:
            notes.append(f"Missing core analysis components: {', '.join(missing)}")
            return ValidationResult(
                is_calibrated=False,
                overall_score=None,
                confidence_score=pdata.step08_confidence or 0.5,
                status_label="Overall score unavailable",
                report_status="partial",
                missing_components=missing,
                validation_notes=notes
            )

        # 4. Calibrated overall score calculation (4 pillars equal 25% weight)
        calibrated_overall = round(
            (0.25 * pdata.grammar_score) +
            (0.25 * pdata.vocabulary_score) +
            (0.25 * pdata.fluency_score) +
            (0.25 * pdata.pronunciation_score),
            1
        )

        # Confidence blending
        conf_values = [c for c in [pdata.step08_confidence, pdata.step09_confidence] if c is not None]
        confidence = round(sum(conf_values) / len(conf_values), 2) if conf_values else 0.85

        return ValidationResult(
            is_calibrated=True,
            overall_score=calibrated_overall,
            confidence_score=confidence,
            status_label="Calibrated",
            report_status="completed",
            missing_components=[],
            validation_notes=["All four assessment pillars validated and calibrated."]
        )

