"""
FluentMeet AI - Step 08: Pydantic Schemas for AI English Analysis
Specification: Step 08 - Section 20 & 22
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TriggerAnalysisRequest(BaseModel):
    force_reanalyze: bool = False


class CategoryScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    score: Optional[float] = None
    status: str
    evidence_count: int = 0
    confidence: Optional[float] = None


class GrammarIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    transcript_segment_id: Optional[str] = None
    category: str
    original_text: str
    corrected_text: str
    explanation: str
    rule_name: Optional[str] = None
    suggested_alternative: Optional[str] = None
    severity: str
    confidence: Optional[float] = None
    evidence_status: str


class VocabularyInsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    transcript_segment_id: Optional[str] = None
    original_expression: str
    suggested_expression: str
    explanation: str
    insight_type: str
    context_note: Optional[str] = None
    example_sentence: Optional[str] = None
    confidence: Optional[float] = None


class FluencyMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    metric_name: str
    metric_value: float
    unit: str
    evidence_count: int = 0
    confidence: Optional[float] = None


class CommunicationInsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    insight_type: str
    title: str
    description: str
    evidence: Optional[str] = None
    confidence: Optional[float] = None


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_category: str
    priority: str
    title: str
    actionable_suggestion: str
    evidence_reference: Optional[str] = None
    example: Optional[str] = None
    expected_outcome: Optional[str] = None
    status: str


class ParticipantSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    speaker_id: Optional[str] = None
    participant_id: Optional[str] = None
    speaker_label: str
    overall_score: Optional[float] = None
    score_status: str
    evidence_coverage: float = 1.0
    analysis_confidence: Optional[float] = None
    status: str
    category_scores: List[CategoryScoreResponse] = []


class AnalysisSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meeting_id: str
    status: str
    requested_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message_safe: Optional[str] = None
    participants: List[ParticipantSummaryResponse] = []


class ParticipantDetailedAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_session_id: str
    speaker_id: Optional[str] = None
    participant_id: Optional[str] = None
    speaker_label: str
    overall_score: Optional[float] = None
    score_status: str
    evidence_coverage: float
    analysis_confidence: Optional[float] = None
    status: str
    category_scores: List[CategoryScoreResponse] = []
    grammar_issues: List[GrammarIssueResponse] = []
    vocabulary_insights: List[VocabularyInsightResponse] = []
    fluency_metrics: List[FluencyMetricResponse] = []
    communication_insights: List[CommunicationInsightResponse] = []
    recommendations: List[RecommendationResponse] = []


class HistoricalProgressPoint(BaseModel):
    meeting_id: str
    analysis_session_id: str
    session_date: datetime
    overall_score: Optional[float] = None
    category_scores: List[CategoryScoreResponse] = []


class HistoricalProgressResponse(BaseModel):
    participant_id: Optional[str] = None
    speaker_label: Optional[str] = None
    history: List[HistoricalProgressPoint] = []

