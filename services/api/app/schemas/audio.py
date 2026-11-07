"""
FluentMeet AI - Audio Ingestion Schemas
Specification: Step 06 - Section 18
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AudioStreamCreate(BaseModel):
    source_id: int = Field(..., ge=0, le=1, description="0=Remote Meeting Audio, 1=Local Microphone Audio")
    codec: str = Field("pcm_s16le", description="Audio codec format")
    sample_rate: int = Field(16000, description="Target sample rate in Hz")
    channels: int = Field(1, description="Audio channel count (1=Mono)")
    organization_id: Optional[str] = None

class AudioStreamResponse(BaseModel):
    id: str
    meeting_id: str
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    source_id: int
    stream_id: str
    sample_rate: int
    channels: int
    encoding: str
    stream_status: str
    status: Optional[str] = None
    codec: Optional[str] = None
    total_packets: Optional[int] = 0
    total_samples: Optional[int] = 0
    total_duration_ms: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AudioQualityMetricResponse(BaseModel):
    rms_level: float
    peak_amplitude: float
    clipping_ratio: float
    silence_ratio: float
    invalid_sample_count: int
    duration_ms: int
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AudioSegmentResponse(BaseModel):
    id: str
    meeting_id: str
    stream_id: str
    source_id: int
    start_timestamp: float
    end_timestamp: float
    first_sequence: int
    last_sequence: int
    sample_rate: int
    channels: int
    encoding: str
    sample_count: int
    duration_ms: int
    checksum: str
    storage_key: str
    storage_status: str
    processing_status: str
    created_at: datetime
    quality_metric: Optional[AudioQualityMetricResponse] = None

    model_config = ConfigDict(from_attributes=True)

class AudioMeetingStatusResponse(BaseModel):
    meeting_id: str
    status: str
    active_sources: List[int]
    source_stats: Dict[int, Dict[str, Any]]
    total_segments: int
    total_duration_ms: int
    total_bytes: int
    total_gaps_detected: int

class AudioMeetingQualityResponse(BaseModel):
    meeting_id: str
    overall_quality: str
    total_segments_analyzed: int
    average_rms: float
    peak_amplitude: float
    average_clipping_ratio: float
    average_silence_ratio: float
    degraded_segments_count: int
    details_by_source: Dict[int, Dict[str, Any]]
