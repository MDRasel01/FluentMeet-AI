from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ParticipantCreate(BaseModel):
    name: str
    is_local_user: bool = False

class MeetingCreateRequest(BaseModel):
    title: str
    platform: str
    meeting_url: Optional[str] = None
    consent_confirmed: bool = False
    participants: Optional[List[ParticipantCreate]] = []

class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    platform: str
    meeting_url: Optional[str]
    status: str
    duration_seconds: int
    my_speaking_seconds: int
    overall_score: Optional[int]
    started_at: datetime
