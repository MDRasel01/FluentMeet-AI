"""
FluentMeet AI - Step 10 Pydantic Schemas: Dashboard Analytics
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DashboardRecentMeetingItem(BaseModel):
    meeting_id: str
    title: str
    date: datetime
    duration_seconds: float
    participants_count: int
    average_score: Optional[float] = None
    report_id: Optional[str] = None
    status: str = "completed"


class DashboardSummaryResponse(BaseModel):
    total_meetings_analyzed: int = 0
    total_speaking_hours: float = 0.0
    average_english_score: Optional[float] = None
    ielts_average_band: Optional[float] = None
    top_recurring_grammar_errors: List[Dict[str, Any]] = Field(default_factory=list)
    top_vocabulary_enhancement_areas: List[Dict[str, Any]] = Field(default_factory=list)
    active_participants_count: int = 0


class DashboardTrendsResponse(BaseModel):
    dates: List[str] = Field(default_factory=list)
    overall_scores: List[Optional[float]] = Field(default_factory=list)
    grammar_scores: List[Optional[float]] = Field(default_factory=list)
    vocabulary_scores: List[Optional[float]] = Field(default_factory=list)
    fluency_scores: List[Optional[float]] = Field(default_factory=list)
    pronunciation_scores: List[Optional[float]] = Field(default_factory=list)

