"""
FluentMeet AI - Step 10: Report Generation & Retrieval REST Endpoints
Specification: Step 10 - Technical Implementation Specification
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User, Meeting
from app.models.report import ReportSnapshot
from app.schemas.common import ApiResponse
from app.schemas.report import (
    GenerateReportRequest,
    ReportSnapshotResponse,
    HistoricalComparisonResponse,
    ExportReportRequest,
    ExportReportResponse,
)
from app.reports.orchestrator import ReportOrchestrator
from app.reports.history import HistoricalProgressService
from app.reports.export import ReportExportService

logger = logging.getLogger("api.reports")
router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


async def _verify_meeting_access(meeting_id: str, current_user: User, db: AsyncSession) -> Meeting:
    """
    Enforces tenant and user isolation boundaries for meetings.
    """
    res = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    user_org_id = getattr(current_user, "current_organization_id", None)
    if meeting.user_id != current_user.id and (not user_org_id or meeting.organization_id != user_org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to meeting reports",
        )
    return meeting


@router.post("/generate", response_model=ApiResponse[List[ReportSnapshotResponse]])
async def generate_reports(
    payload: GenerateReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates immutable report snapshots for a meeting (summary + participants).
    """
    await _verify_meeting_access(payload.meeting_id, current_user, db)

    try:
        result = await ReportOrchestrator.generate_meeting_reports(
            db=db,
            meeting_id=payload.meeting_id,
            user_id=current_user.id,
            tenant_id=getattr(current_user, "current_organization_id", None),
            force_regenerate=payload.force_regenerate or False,
            scoring_rubric_version=payload.scoring_rubric_version or "1.0",
        )
        all_snapshots = []
        if result.meeting_summary_snapshot:
            all_snapshots.append(result.meeting_summary_snapshot)
        all_snapshots.extend(result.participant_snapshots)

        return ApiResponse.ok_response(data=all_snapshots)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as exc:
        logger.exception(f"Report generation failed for meeting {payload.meeting_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/meetings/{meeting_id}", response_model=ApiResponse[ReportSnapshotResponse])
async def get_meeting_summary_report(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the latest meeting summary report snapshot.
    """
    await _verify_meeting_access(meeting_id, current_user, db)

    res = await db.execute(
        select(ReportSnapshot)
        .where(
            ReportSnapshot.meeting_id == meeting_id,
            ReportSnapshot.report_type == "meeting_summary"
        )
        .order_by(ReportSnapshot.report_version.desc())
    )
    snapshot = res.scalars().first()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting summary report not found")

    return ApiResponse.ok_response(data=snapshot)


@router.get("/meetings/{meeting_id}/participants", response_model=ApiResponse[List[ReportSnapshotResponse]])
async def get_meeting_participant_reports(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves individual participant reports for a meeting.
    """
    await _verify_meeting_access(meeting_id, current_user, db)

    res = await db.execute(
        select(ReportSnapshot)
        .where(
            ReportSnapshot.meeting_id == meeting_id,
            ReportSnapshot.report_type == "individual_participant"
        )
        .order_by(ReportSnapshot.report_version.desc())
    )
    snapshots = res.scalars().all()
    return ApiResponse.ok_response(data=snapshots)


@router.get("/participants/{participant_id}", response_model=ApiResponse[ReportSnapshotResponse])
async def get_participant_report(
    participant_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the latest report snapshot for a specific participant.
    """
    res = await db.execute(
        select(ReportSnapshot)
        .where(
            ReportSnapshot.participant_id == participant_id,
            ReportSnapshot.report_type == "individual_participant"
        )
        .order_by(ReportSnapshot.generated_at.desc())
    )
    snapshot = res.scalars().first()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant report not found")

    await _verify_meeting_access(snapshot.meeting_id, current_user, db)
    return ApiResponse.ok_response(data=snapshot)


@router.get("/{report_id}", response_model=ApiResponse[ReportSnapshotResponse])
async def get_report_by_id(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves a report snapshot by its unique ID.
    """
    res = await db.execute(select(ReportSnapshot).where(ReportSnapshot.id == report_id))
    snapshot = res.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report snapshot not found")

    await _verify_meeting_access(snapshot.meeting_id, current_user, db)
    return ApiResponse.ok_response(data=snapshot)


@router.get("/{report_id}/status", response_model=ApiResponse[dict])
async def get_report_status(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves status of a report.
    """
    res = await db.execute(select(ReportSnapshot).where(ReportSnapshot.id == report_id))
    snapshot = res.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report snapshot not found")

    await _verify_meeting_access(snapshot.meeting_id, current_user, db)
    return ApiResponse.ok_response(data={
        "report_id": snapshot.id,
        "meeting_id": snapshot.meeting_id,
        "report_type": snapshot.report_type,
        "status": snapshot.report_status,
        "overall_score": snapshot.overall_score,
        "generated_at": snapshot.generated_at,
    })


@router.get("/participants/{participant_id}/history", response_model=ApiResponse[HistoricalComparisonResponse])
async def get_participant_historical_trends(
    participant_id: str,
    limit: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves historical performance trends, recurring mistakes, and persistent strengths.
    """
    history = await HistoricalProgressService.get_participant_history(db=db, participant_id=participant_id, limit=limit)
    return ApiResponse.ok_response(data=history)


@router.post("/{report_id}/export/csv")
async def export_report_csv(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates and returns a sanitized CSV document for spreadsheet viewing.
    """
    res = await db.execute(select(ReportSnapshot).where(ReportSnapshot.id == report_id))
    snapshot = res.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report snapshot not found")

    await _verify_meeting_access(snapshot.meeting_id, current_user, db)
    csv_content = await ReportExportService.export_csv(db, snapshot, user_id=current_user.id)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="fluentmeet-report-{report_id[:8]}.csv"'}
    )


@router.post("/{report_id}/export/html")
async def export_report_html(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates and returns a styled, print-optimized HTML document.
    """
    res = await db.execute(select(ReportSnapshot).where(ReportSnapshot.id == report_id))
    snapshot = res.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report snapshot not found")

    await _verify_meeting_access(snapshot.meeting_id, current_user, db)
    html_content = await ReportExportService.export_html(db, snapshot, user_id=current_user.id)

    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'inline; filename="fluentmeet-report-{report_id[:8]}.html"'}
    )

