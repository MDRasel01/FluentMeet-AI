from typing import Dict, Optional
from pydantic import BaseModel

class HealthLiveResponse(BaseModel):
    status: str
    service: str
    environment: str

class HealthReadyResponse(BaseModel):
    status: str
    service: str
    database: str
    redis: str
    dependencies_healthy: bool

