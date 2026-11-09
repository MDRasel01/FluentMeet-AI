"""
FluentMeet AI - Step 10: Dashboard Analytics REST Endpoints
Specification: Step 10 - Technical Implementation Specification
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User
from app.schemas.common import ApiResponse
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DashboardTrendsResponse,
    DashboardRecentMeetingItem,
)
from app.reports.analytics import DashboardAnalyticsService

logger = logging.getLogger("api.dashboard")
router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get("/summary", response_model=ApiResponse[DashboardSummaryResponse])
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns executive KPI cards for the user's dashboard.
    """
    tenant_id = getattr(current_user, "current_organization_id", None)
    summary = await DashboardAnalyticsService.get_dashboard_summary(
        db=db,
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
    return ApiResponse.ok_response(data=summary)


@router.get("/trends", response_model=ApiResponse[DashboardTrendsResponse])
async def get_dashboard_trends(
    limit: int = Query(default=15, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns historical score trends across meetings.
    """
    tenant_id = getattr(current_user, "current_organization_id", None)
    trends = await DashboardAnalyticsService.get_dashboard_trends(
        db=db,
        tenant_id=tenant_id,
        limit=limit,
    )
    return ApiResponse.ok_response(data=trends)


@router.get("/recent-meetings", response_model=ApiResponse[List[DashboardRecentMeetingItem]])
async def get_recent_meetings(
    limit: int = Query(default=10, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns list of recent meetings with report status and summary scores.
    """
    tenant_id = getattr(current_user, "current_organization_id", None)
    meetings = await DashboardAnalyticsService.get_recent_meetings(
        db=db,
        tenant_id=tenant_id,
        limit=limit,
    )
    return ApiResponse.ok_response(data=meetings)
