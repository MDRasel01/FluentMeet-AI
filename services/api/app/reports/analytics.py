"""
FluentMeet AI - Step 10: Dashboard Analytics Service
Powers executive summary cards, historical trend charts, and recent meeting activity feeds.
"""

from typing import Dict, Any, List, Optional
from collections import Counter
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.base import Meeting
from app.models.report import ReportSnapshot
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DashboardTrendsResponse,
    DashboardRecentMeetingItem,
)


class DashboardAnalyticsService:
    """
    Computes dashboard analytics from stored immutable ReportSnapshots.
    """

    @classmethod
    async def get_dashboard_summary(
        cls,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> DashboardSummaryResponse:
        """
        Computes high-level KPI cards for the dashboard.
        """
        stmt = select(ReportSnapshot).where(
            ReportSnapshot.report_type == "individual_participant",
            ReportSnapshot.report_status == "completed"
        )
        if tenant_id:
            stmt = stmt.where(ReportSnapshot.tenant_id == tenant_id)

        res = await db.execute(stmt)
        snapshots = res.scalars().all()

        if not snapshots:
            return DashboardSummaryResponse()

        # Unique meetings
        meeting_ids = {s.meeting_id for s in snapshots}
        total_meetings = len(meeting_ids)

        # Speaking duration & words
        total_speaking_seconds = sum(s.speaking_duration_seconds or 0.0 for s in snapshots)
        total_speaking_hours = round(total_speaking_seconds / 3600.0, 2)

        # Average score
        valid_scores = [s.overall_score for s in snapshots if s.overall_score is not None]
        avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else None

        # Distinct participants
        distinct_participants = {s.participant_id for s in snapshots if s.participant_id}

        # IELTS bands & grammar errors
        ielts_bands = []
        grammar_rules = []
        vocab_areas = []

        for s in snapshots:
            payload = s.report_payload or {}
            ielts = payload.get("ielts_estimate")
            if ielts and ielts.get("overall_band_estimate"):
                ielts_bands.append(ielts["overall_band_estimate"])

            grammar = payload.get("grammar_analysis", {})
            for iss in grammar.get("issues", []):
                rule = iss.get("rule_type")
                if rule:
                    grammar_rules.append(rule)

            vocab = payload.get("vocabulary_analysis", {})
            insights = vocab.get("insights", {})
            for word in insights.get("repetitive_words", []):
                vocab_areas.append(f"Overused word: '{word}'")

        avg_ielts = round(sum(ielts_bands) / len(ielts_bands), 1) if ielts_bands else None

        top_grammar = [
            {"rule": rule, "count": count}
            for rule, count in Counter(grammar_rules).most_common(5)
        ]

        top_vocab = [
            {"area": area, "count": count}
            for area, count in Counter(vocab_areas).most_common(5)
        ]

        return DashboardSummaryResponse(
            total_meetings_analyzed=total_meetings,
            total_speaking_hours=total_speaking_hours,
            average_english_score=avg_score,
            ielts_average_band=avg_ielts,
            top_recurring_grammar_errors=top_grammar,
            top_vocabulary_enhancement_areas=top_vocab,
            active_participants_count=len(distinct_participants),
        )

    @classmethod
    async def get_dashboard_trends(
        cls,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        limit: int = 15,
    ) -> DashboardTrendsResponse:
        """
        Extracts historical trend series across meetings.
        """
        stmt = select(ReportSnapshot).where(
            ReportSnapshot.report_type == "meeting_summary",
            ReportSnapshot.report_status == "completed"
        )
        if tenant_id:
            stmt = stmt.where(ReportSnapshot.tenant_id == tenant_id)

        res = await db.execute(stmt.order_by(ReportSnapshot.generated_at.asc()).limit(limit))
        snapshots = res.scalars().all()

        dates: List[str] = []
        overall_scores: List[Optional[float]] = []
        grammar_scores: List[Optional[float]] = []
        vocabulary_scores: List[Optional[float]] = []
        fluency_scores: List[Optional[float]] = []
        pronunciation_scores: List[Optional[float]] = []

        for s in snapshots:
            dates.append(s.generated_at.strftime("%b %d"))
            overall_scores.append(s.overall_score)
            grammar_scores.append(s.overall_score)
            vocabulary_scores.append(s.overall_score)
            fluency_scores.append(s.overall_score)
            pronunciation_scores.append(s.overall_score)

        return DashboardTrendsResponse(
            dates=dates,
            overall_scores=overall_scores,
            grammar_scores=grammar_scores,
            vocabulary_scores=vocabulary_scores,
            fluency_scores=fluency_scores,
            pronunciation_scores=pronunciation_scores,
        )

    @classmethod
    async def get_recent_meetings(
        cls,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[DashboardRecentMeetingItem]:
        """
        Retrieves recent meetings with their snapshot status and summary.
        """
        stmt = select(Meeting).order_by(Meeting.created_at.desc())
        if tenant_id:
            stmt = stmt.where(Meeting.organization_id == tenant_id)

        res = await db.execute(stmt.limit(limit))
        meetings = res.scalars().all()
        results: List[DashboardRecentMeetingItem] = []

        for m in meetings:
            res_snap = await db.execute(
                select(ReportSnapshot)
                .where(
                    ReportSnapshot.meeting_id == m.id,
                    ReportSnapshot.report_type == "meeting_summary"
                )
                .order_by(ReportSnapshot.report_version.desc())
            )
            snapshot = res_snap.scalars().first()

            score = snapshot.overall_score if snapshot else None
            status = snapshot.report_status if snapshot else "pending"
            rep_id = snapshot.id if snapshot else None

            payload = (snapshot.report_payload if snapshot else {}) or {}
            metrics = payload.get("summary_metrics", {})
            participants_count = metrics.get("participant_count", 0)
            dur = metrics.get("total_duration_seconds", 0.0)

            results.append(
                DashboardRecentMeetingItem(
                    meeting_id=m.id,
                    title=m.title or f"Meeting {m.id[:8]}",
                    date=m.created_at,
                    duration_seconds=dur,
                    participants_count=participants_count,
                    average_score=score,
                    report_id=rep_id,
                    status=status,
                )
            )

        return results
