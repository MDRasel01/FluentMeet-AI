"""
FluentMeet AI - Transcript & Speaker Schemas
Specification: Step 07 - Section 8 & Section 18
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class TranscriptWordResponse(BaseModel):
    id: Optional[str] = None
    word: str
    start_time_ms: int
    end_time_ms: int
    confidence_score: Optional[float] = None
    speaker_id: Optional[str] = None
    word_index: int = 0

class TranscriptSegmentResponse(BaseModel):
    id: str
    meeting_id: str
    speaker_id: Optional[str] = None
    speaker_label: Optional[str] = None
    speaker_name: Optional[str] = None
    source_id: int = 0
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    text: str
    language: str = "en"
    confidence_score: Optional[float] = None
    status: str = "final"
    revision_number: int = 1
    words: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None

class TranscriptCorrectionRequest(BaseModel):
    text: Optional[str] = None
    speaker_id: Optional[str] = None

class MeetingSpeakerResponse(BaseModel):
    id: str
    meeting_id: str
    speaker_label: str
    display_name: Optional[str] = None
    is_identified: bool = False
    confidence_score: Optional[float] = None
    source_id: Optional[int] = None

class SpeakerUpdateRequest(BaseModel):
    display_name: str
    participant_id: Optional[str] = None

class SpeechOverlapResponse(BaseModel):
    id: str
    meeting_id: str
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    overlapping_speaker_ids: List[str]
    confidence_score: Optional[float] = None
