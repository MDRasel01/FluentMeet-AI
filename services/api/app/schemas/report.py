"""
FluentMeet AI - Step 10 Pydantic Schemas: Report Generation, Analytics & Dashboard
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class GenerateReportRequest(BaseModel):
    meeting_id: str
    report_types: Optional[List[str]] = Field(default=["meeting_summary", "individual_participant"])
    participant_ids: Optional[List[str]] = None
    scoring_rubric_version: Optional[str] = "1.0"
    force_regenerate: Optional[bool] = False


class ReportSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meeting_id: str
    tenant_id: Optional[str] = None
    report_type: str
    participant_id: Optional[str] = None
    speaker_label: Optional[str] = None
    report_version: int = 1
    report_status: str
    overall_score: Optional[float] = None
    confidence_score: Optional[float] = None
    word_count: int = 0
    speaking_duration_seconds: float = 0.0
    source_analysis_version: str = "1.0"
    scoring_rubric_version: str = "1.0"
    report_payload: Dict[str, Any]
    generated_at: datetime
    created_at: datetime


class MeetingReportSummaryResponse(BaseModel):
    meeting_id: str
    title: Optional[str] = None
    meeting_date: Optional[datetime] = None
    duration_seconds: float = 0.0
    total_words: int = 0
    participant_count: int = 0
    average_overall_score: Optional[float] = None
    participants: List[Dict[str, Any]] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    communication_dynamics: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime


class ParticipantReportDetailResponse(BaseModel):
    report_id: str
    meeting_id: str
    participant_id: Optional[str] = None
    speaker_label: str
    overall_score: Optional[float] = None
    confidence_score: Optional[float] = None
    status_label: str = "Calibrated"
    word_count: int = 0
    speaking_duration_seconds: float = 0.0
    grammar_analysis: Dict[str, Any] = Field(default_factory=dict)
    vocabulary_analysis: Dict[str, Any] = Field(default_factory=dict)
    fluency_analysis: Dict[str, Any] = Field(default_factory=dict)
    pronunciation_analysis: Dict[str, Any] = Field(default_factory=dict)
    ielts_estimate: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    ielts_disclaimer: str = (
        "Educational practice estimate only. This is not an official IELTS score, "
        "certified assessment, or substitute for an IELTS examiner."
    )


class HistoricalComparisonPoint(BaseModel):
    meeting_id: str
    meeting_date: datetime
    report_id: str
    overall_score: Optional[float] = None
    grammar_score: Optional[float] = None
    vocabulary_score: Optional[float] = None
    fluency_score: Optional[float] = None
    pronunciation_score: Optional[float] = None
    ielts_overall_band: Optional[float] = None
    word_count: int = 0


class HistoricalComparisonResponse(BaseModel):
    participant_id: str
    speaker_name: Optional[str] = None
    total_meetings: int
    history_points: List[HistoricalComparisonPoint] = Field(default_factory=list)
    trends: Dict[str, Any] = Field(default_factory=dict)
    recurring_mistakes: List[Dict[str, Any]] = Field(default_factory=list)
    persistent_strengths: List[str] = Field(default_factory=list)


class ExportReportRequest(BaseModel):
    format: str = Field(default="pdf", description="'pdf', 'csv', or 'html'")
    include_transcripts: Optional[bool] = True
    include_pronunciation_details: Optional[bool] = True


class ExportReportResponse(BaseModel):
    export_id: str
    report_snapshot_id: str
    format: str
    download_url: Optional[str] = None
    content: Optional[str] = None
    file_size_bytes: Optional[int] = None
    expires_at: Optional[datetime] = None

