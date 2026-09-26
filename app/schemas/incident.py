from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    severity: Severity
    status: IncidentStatus = IncidentStatus.OPEN
    service: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)


class Incident(IncidentCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }