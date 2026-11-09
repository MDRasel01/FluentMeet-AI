"""
FluentMeet AI - Step 10: Historical Performance & Progress Service
Compares participant report snapshots over time, tracks rubric compatibility, and identifies recurring mistakes.
"""

from typing import Dict, Any, List, Optional
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.report import ReportSnapshot
from app.schemas.report import HistoricalComparisonResponse, HistoricalComparisonPoint


class HistoricalProgressService:
    """
    Analyzes historical trajectories across multiple meetings for a participant.
    """

    @classmethod
    async def get_participant_history(
        cls,
        db: AsyncSession,
        participant_id: str,
        limit: int = 20,
    ) -> HistoricalComparisonResponse:
        """
        Retrieves and analyzes past ReportSnapshots for a participant.
        """
        res = await db.execute(
            select(ReportSnapshot)
            .where(
                ReportSnapshot.participant_id == participant_id,
                ReportSnapshot.report_type == "individual_participant",
                ReportSnapshot.report_status == "completed"
            )
            .order_by(ReportSnapshot.generated_at.asc())
            .limit(limit)
        )
        snapshots = res.scalars().all()

        if not snapshots:
            return HistoricalComparisonResponse(
                participant_id=participant_id,
                speaker_name=None,
                total_meetings=0,
                history_points=[],
                trends={"status": "no_data", "message": "No historical report snapshots found."},
                recurring_mistakes=[],
                persistent_strengths=[]
            )

        speaker_name = None
        history_points: List[HistoricalComparisonPoint] = []
        all_grammar_issues: List[str] = []
        high_score_categories = Counter()

        for s in snapshots:
            payload = s.report_payload or {}
            meta = payload.get("metadata", {})
            if not speaker_name:
                speaker_name = meta.get("display_name") or meta.get("speaker_label")

            perf = payload.get("overall_performance", {})
            grammar = payload.get("grammar_analysis", {})
            vocab = payload.get("vocabulary_analysis", {})
            fluency = payload.get("fluency_analysis", {})
            pron = payload.get("pronunciation_analysis", {})
            ielts = payload.get("ielts_estimate") or {}

            g_score = grammar.get("score")
            v_score = vocab.get("score")
            f_score = fluency.get("score")
            p_score = pron.get("score")

            if g_score and g_score >= 80:
                high_score_categories["Grammar"] += 1
            if v_score and v_score >= 80:
                high_score_categories["Vocabulary"] += 1
            if f_score and f_score >= 80:
                high_score_categories["Fluency"] += 1
            if p_score and p_score >= 80:
                high_score_categories["Pronunciation"] += 1

            for iss in grammar.get("issues", []):
                rule = iss.get("rule_type") or "grammar_rule"
                all_grammar_issues.append(rule)

            history_points.append(
                HistoricalComparisonPoint(
                    meeting_id=s.meeting_id,
                    meeting_date=s.generated_at,
                    report_id=s.id,
                    overall_score=perf.get("overall_score"),
                    grammar_score=g_score,
                    vocabulary_score=v_score,
                    fluency_score=f_score,
                    pronunciation_score=p_score,
                    ielts_overall_band=ielts.get("overall_band_estimate"),
                    word_count=payload.get("speaking_metrics", {}).get("total_words", 0),
                )
            )

        # Check for minimum threshold of 2 meetings
        if len(history_points) < 2:
            trends = {
                "status": "baseline_only",
                "message": "At least 2 meetings are required to compute historical growth trends.",
                "overall_delta": 0.0,
            }
        else:
            first_score = next((p.overall_score for p in history_points if p.overall_score is not None), None)
            last_score = next((p.overall_score for p in reversed(history_points) if p.overall_score is not None), None)
            delta = round(last_score - first_score, 1) if (first_score is not None and last_score is not None) else None

            trajectory = "steady"
            if delta is not None:
                if delta >= 3.0:
                    trajectory = "improving"
                elif delta <= -3.0:
                    trajectory = "declining"

            trends = {
                "status": "active",
                "trajectory": trajectory,
                "overall_delta": delta,
                "first_meeting_score": first_score,
                "latest_meeting_score": last_score,
            }

        # Recurring grammar mistakes (appearing >= 2 times)
        issue_counts = Counter(all_grammar_issues)
        recurring_mistakes = [
            {"rule_type": rule, "frequency": count}
            for rule, count in issue_counts.most_common(5)
            if count >= 2
        ]

        # Persistent strengths (present in at least 50% of meetings)
        threshold = max(1, len(history_points) // 2)
        persistent_strengths = [
            cat for cat, count in high_score_categories.items() if count >= threshold
        ]

        return HistoricalComparisonResponse(
            participant_id=participant_id,
            speaker_name=speaker_name,
            total_meetings=len(history_points),
            history_points=history_points,
            trends=trends,
            recurring_mistakes=recurring_mistakes,
            persistent_strengths=persistent_strengths
        )
