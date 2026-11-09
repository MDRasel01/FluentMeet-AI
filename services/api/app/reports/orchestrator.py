"""
FluentMeet AI - Step 10: Report Generation Orchestrator
Coordinates multi-source data ingestion, validation, snapshot persistence, and event emission.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.base import Meeting
from app.models.report import ReportSnapshot, ReportAccessLog
from app.reports.collector import ReportDataCollector
from app.reports.validator import ReportValidationEngine
from app.reports.builder import ParticipantReportBuilder, MeetingReportBuilder


class ReportOrchestrationResult:
    def __init__(
        self,
        meeting_summary_snapshot: Optional[ReportSnapshot],
        participant_snapshots: List[ReportSnapshot],
        is_idempotent_replay: bool = False,
    ):
        self.meeting_summary_snapshot = meeting_summary_snapshot
        self.participant_snapshots = participant_snapshots
        self.is_idempotent_replay = is_idempotent_replay


class ReportOrchestrator:
    """
    Main orchestrator for generating, validating, and persisting immutable reports.
    """

    @classmethod
    async def generate_meeting_reports(
        cls,
        db: AsyncSession,
        meeting_id: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        force_regenerate: bool = False,
        scoring_rubric_version: str = "1.0",
    ) -> ReportOrchestrationResult:
        """
        Coordinates end-to-end report generation for a meeting.
        """
        res = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = res.scalar_one_or_none()
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found.")

        effective_tenant = tenant_id or getattr(meeting, "organization_id", None)

        # 1. Idempotency check: if completed snapshots exist and force_regenerate is False
        if not force_regenerate:
            res = await db.execute(
                select(ReportSnapshot)
                .where(
                    ReportSnapshot.meeting_id == meeting_id,
                    ReportSnapshot.report_type == "meeting_summary",
                    ReportSnapshot.report_status == "completed"
                )
                .order_by(ReportSnapshot.report_version.desc())
            )
            existing_summary = res.scalars().first()

            if existing_summary:
                res = await db.execute(
                    select(ReportSnapshot).where(
                        ReportSnapshot.meeting_id == meeting_id,
                        ReportSnapshot.report_type == "individual_participant",
                        ReportSnapshot.report_version == existing_summary.report_version
                    )
                )
                existing_participants = res.scalars().all()
                return ReportOrchestrationResult(
                    meeting_summary_snapshot=existing_summary,
                    participant_snapshots=existing_participants,
                    is_idempotent_replay=True,
                )

        # Determine next report version
        res = await db.execute(
            select(ReportSnapshot.report_version)
            .where(ReportSnapshot.meeting_id == meeting_id)
            .order_by(ReportSnapshot.report_version.desc())
        )
        latest_version = res.scalars().first()
        next_version = (latest_version + 1) if latest_version else 1

        # 2. Collect multi-source data
        collected = await ReportDataCollector.collect_meeting_data(db, meeting_id)
        if not collected or not collected["participants_data"]:
            raise ValueError(f"No participant data available for meeting {meeting_id}.")

        participants_data = collected["participants_data"]
        participant_snapshots: List[ReportSnapshot] = []
        participant_payloads: List[Dict[str, Any]] = []

        now_utc = datetime.now(timezone.utc)

        # 3. Process each participant
        for label, pdata in participants_data.items():
            val = ReportValidationEngine.validate_participant(pdata, scoring_rubric_version)
            payload = ParticipantReportBuilder.build(
                pdata=pdata,
                val=val,
                meeting_id=meeting_id,
                scoring_rubric_version=scoring_rubric_version,
            )
            participant_payloads.append(payload)

            p_snapshot = ReportSnapshot(
                tenant_id=effective_tenant,
                meeting_id=meeting_id,
                report_type="individual_participant",
                participant_id=pdata.participant_id,
                speaker_label=label,
                report_version=next_version,
                report_status=val.report_status,
                source_analysis_version="1.0",
                source_analysis_references={
                    "total_words": pdata.total_words,
                    "duration_s": pdata.speaking_duration_seconds,
                    "has_pronunciation": pdata.pronunciation_score is not None,
                },
                scoring_rubric_version=scoring_rubric_version,
                overall_score=val.overall_score,
                confidence_score=val.confidence_score,
                word_count=pdata.total_words,
                speaking_duration_seconds=pdata.speaking_duration_seconds,
                report_payload=payload,
                generated_at=now_utc,
                created_by=user_id,
            )
            db.add(p_snapshot)
            participant_snapshots.append(p_snapshot)

        # 4. Build Meeting Summary
        summary_payload = MeetingReportBuilder.build(
            meeting_id=meeting_id,
            title=meeting.title or f"Meeting {meeting_id[:8]}",
            meeting_date=meeting.created_at,
            participant_reports=participant_payloads,
            scoring_rubric_version=scoring_rubric_version,
        )

        meeting_summary_snapshot = ReportSnapshot(
            tenant_id=effective_tenant,
            meeting_id=meeting_id,
            report_type="meeting_summary",
            participant_id=None,
            speaker_label=None,
            report_version=next_version,
            report_status="completed",
            source_analysis_version="1.0",
            source_analysis_references={
                "participant_count": len(participant_snapshots),
                "total_words": summary_payload["summary_metrics"]["total_words"],
            },
            scoring_rubric_version=scoring_rubric_version,
            overall_score=summary_payload["summary_metrics"]["average_overall_score"],
            confidence_score=0.9,
            word_count=summary_payload["summary_metrics"]["total_words"],
            speaking_duration_seconds=summary_payload["summary_metrics"]["total_duration_seconds"],
            report_payload=summary_payload,
            generated_at=now_utc,
            created_by=user_id,
        )
        db.add(meeting_summary_snapshot)
        await db.flush()

        # 5. Access Log entry
        access_log = ReportAccessLog(
            tenant_id=effective_tenant,
            report_snapshot_id=meeting_summary_snapshot.id,
            actor_id=user_id,
            action="generate_reports",
            request_metadata={"version": next_version, "participants": len(participant_snapshots)},
        )
        db.add(access_log)

        await db.commit()
        await db.refresh(meeting_summary_snapshot)
        for ps in participant_snapshots:
            await db.refresh(ps)

        # 6. Try publishing Redis event (non-blocking)
        cls._publish_event(meeting_id, next_version)

        return ReportOrchestrationResult(
            meeting_summary_snapshot=meeting_summary_snapshot,
            participant_snapshots=participant_snapshots,
            is_idempotent_replay=False,
        )

    @classmethod
    def _publish_event(cls, meeting_id: str, version: int) -> None:
        try:
            from app.core.redis import get_redis_client
            client = get_redis_client()
            if client:
                event_data = {
                    "event": "report.completed",
                    "meeting_id": meeting_id,
                    "version": version,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                client.xadd("report:events", {"payload": json.dumps(event_data)})
        except Exception:
            # Redis event publication is best-effort
            pass
