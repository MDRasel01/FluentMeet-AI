"""
FluentMeet AI - Step 10: Structured Report Payload Builders
Builds immutable JSON payloads for Individual Participant Reports and Meeting Summary Reports.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.reports.collector import CollectedParticipantData
from app.reports.validator import ValidationResult


MANDATORY_IELTS_DISCLAIMER = (
    "Educational practice estimate only. This is not an official IELTS score, "
    "certified assessment, or substitute for an IELTS examiner."
)


class ParticipantReportBuilder:
    """
    Constructs the detailed individual participant report payload.
    """

    @classmethod
    def build(
        cls,
        pdata: CollectedParticipantData,
        val: ValidationResult,
        meeting_id: str,
        scoring_rubric_version: str = "1.0",
    ) -> Dict[str, Any]:
        # Compute speaking pace / WPM
        duration_min = pdata.speaking_duration_seconds / 60.0 if pdata.speaking_duration_seconds > 0 else 0.0
        wpm = round(pdata.total_words / duration_min, 1) if duration_min > 0 else 0.0

        # Consolidate recommendations
        all_recs = []
        for r in pdata.step08_recommendations:
            all_recs.append({
                "source": "english_analysis",
                "category": r.get("category", "General"),
                "priority": r.get("priority", "medium"),
                "recommendation_text": r.get("recommendation_text", ""),
                "practice_text": None,
            })
        for pr in pdata.pronunciation_recommendations:
            all_recs.append({
                "source": "pronunciation",
                "category": f"Pronunciation: {pr.get('drill_type', 'Drill')}",
                "priority": "high",
                "recommendation_text": f"{pr.get('title', '')}: {pr.get('explanation', '')}",
                "practice_text": pr.get("practice_text"),
            })

        # IELTS payload with disclaimer
        ielts_payload = None
        if pdata.ielts_assessment:
            ielts_payload = {
                **pdata.ielts_assessment,
                "disclaimer": MANDATORY_IELTS_DISCLAIMER,
            }

        return {
            "metadata": {
                "meeting_id": meeting_id,
                "participant_id": pdata.participant_id,
                "speaker_label": pdata.speaker_label,
                "display_name": pdata.display_name,
                "scoring_rubric_version": scoring_rubric_version,
                "report_type": "individual_participant",
            },
            "overall_performance": {
                "overall_score": val.overall_score,
                "confidence_score": val.confidence_score,
                "status_label": val.status_label,
                "report_status": val.report_status,
                "is_calibrated": val.is_calibrated,
                "missing_components": val.missing_components,
                "validation_notes": val.validation_notes,
            },
            "speaking_metrics": {
                "total_words": pdata.total_words,
                "speaking_duration_seconds": round(pdata.speaking_duration_seconds, 1),
                "words_per_minute": wpm,
            },
            "grammar_analysis": {
                "score": pdata.grammar_score,
                "issues_count": len(pdata.grammar_issues),
                "issues": pdata.grammar_issues,
            },
            "vocabulary_analysis": {
                "score": pdata.vocabulary_score,
                "insights": pdata.vocabulary_insights or {
                    "lexical_diversity": None,
                    "high_impact_words": [],
                    "repetitive_words": [],
                },
            },
            "fluency_analysis": {
                "score": pdata.fluency_score,
                "metrics": pdata.fluency_metrics or {
                    "words_per_minute": wpm,
                    "filler_word_count": 0,
                    "pause_count": 0,
                    "speech_rate_category": "moderate",
                },
            },
            "pronunciation_analysis": {
                "score": pdata.pronunciation_score,
                "confidence": pdata.step09_confidence,
                "mispronounced_words": pdata.mispronounced_words,
                "prosody": pdata.prosody or {},
            },
            "ielts_estimate": ielts_payload,
            "recommendations": all_recs,
            "disclaimers": {
                "ielts": MANDATORY_IELTS_DISCLAIMER,
                "scoring": "Scores reflect spoken English communication patterns observed during this recording.",
            },
        }


class MeetingReportBuilder:
    """
    Constructs the aggregate meeting summary report payload.
    """

    @classmethod
    def build(
        cls,
        meeting_id: str,
        title: str,
        meeting_date: Optional[datetime],
        participant_reports: List[Dict[str, Any]],
        scoring_rubric_version: str = "1.0",
    ) -> Dict[str, Any]:
        total_duration = sum(r["speaking_metrics"]["speaking_duration_seconds"] for r in participant_reports)
        total_words = sum(r["speaking_metrics"]["total_words"] for r in participant_reports)

        # Average score across calibrated participants only
        calibrated_scores = [
            r["overall_performance"]["overall_score"]
            for r in participant_reports
            if r["overall_performance"]["overall_score"] is not None
        ]
        avg_score = round(sum(calibrated_scores) / len(calibrated_scores), 1) if calibrated_scores else None

        # Participant summary list with talk time percentages
        participant_summaries = []
        for r in participant_reports:
            dur = r["speaking_metrics"]["speaking_duration_seconds"]
            talk_pct = round((dur / total_duration) * 100.0, 1) if total_duration > 0 else 0.0
            participant_summaries.append({
                "participant_id": r["metadata"]["participant_id"],
                "speaker_label": r["metadata"]["speaker_label"],
                "display_name": r["metadata"]["display_name"],
                "overall_score": r["overall_performance"]["overall_score"],
                "status_label": r["overall_performance"]["status_label"],
                "word_count": r["speaking_metrics"]["total_words"],
                "duration_seconds": dur,
                "talk_time_percentage": talk_pct,
                "ielts_band": (r.get("ielts_estimate") or {}).get("overall_band_estimate"),
            })

        # Dynamic highlights
        highlights = []
        if len(calibrated_scores) > 0 and avg_score is not None:
            if avg_score >= 80:
                highlights.append(f"Strong overall communication across the meeting (Average: {avg_score}/100).")
            elif avg_score >= 60:
                highlights.append(f"Solid conversational English with opportunities for polish (Average: {avg_score}/100).")
            else:
                highlights.append(f"Meeting English communication requires structured development (Average: {avg_score}/100).")
        
        # Team growth areas
        growth_areas = []
        total_grammar_issues = sum(r["grammar_analysis"]["issues_count"] for r in participant_reports)
        if total_grammar_issues > 0:
            growth_areas.append(f"{total_grammar_issues} grammatical structures identified for refinement across speakers.")
        
        total_mispronounced = sum(len(r["pronunciation_analysis"]["mispronounced_words"]) for r in participant_reports)
        if total_mispronounced > 0:
            growth_areas.append(f"{total_mispronounced} words identified with pronunciation variance across participants.")

        return {
            "metadata": {
                "meeting_id": meeting_id,
                "title": title or f"Meeting {meeting_id[:8]}",
                "meeting_date": meeting_date.isoformat() if meeting_date else None,
                "report_type": "meeting_summary",
                "scoring_rubric_version": scoring_rubric_version,
            },
            "summary_metrics": {
                "participant_count": len(participant_reports),
                "total_duration_seconds": round(total_duration, 1),
                "total_words": total_words,
                "average_overall_score": avg_score,
                "calibrated_participants_count": len(calibrated_scores),
            },
            "participants": participant_summaries,
            "communication_balance": {
                "distribution": [
                    {"speaker": p["display_name"], "percentage": p["talk_time_percentage"]}
                    for p in participant_summaries
                ]
            },
            "highlights": highlights,
            "areas_for_team_growth": growth_areas,
            "disclaimers": {
                "summary": "Meeting summary is aggregated strictly from validated participant spoken contributions.",
                "ielts": MANDATORY_IELTS_DISCLAIMER,
            },
        }
