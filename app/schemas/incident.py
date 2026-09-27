from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# Define the Severity enum, which represents the severity levels of an incident. The possible values are LOW, MEDIUM, HIGH, and CRITICAL.
class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# Define the IncidentStatus enum, which represents the status of an incident. The possible values are OPEN, INVESTIGATING, and RESOLVED.
class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"

# Define the IncidentCreate Pydantic model, which represents the data required to create a new incident. It includes fields for title, severity, status, service, and description, with validation constraints on the length of the title, service, and description fields.
class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    severity: Severity
    status: IncidentStatus = IncidentStatus.OPEN
    service: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)

# 
class Incident(IncidentCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }