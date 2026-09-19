from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# Define an enumeration for incident severity levels, which includes LOW, MEDIUM, HIGH, and CRITICAL.
class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Define an enumeration for incident status, which includes OPEN, INVESTIGATING, and RESOLVED.
class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


# Define a Pydantic model for creating an incident, which includes fields for title, severity, status, service, and description. The model also includes validation constraints for the length of the title, service, and description fields.
class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    severity: Severity
    status: IncidentStatus = IncidentStatus.OPEN
    service: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)


# Define a Pydantic model for an incident, which inherits from the IncidentCreate model and adds fields for id and created_at. The created_at field is of type datetime.
class Incident(IncidentCreate):
    id: int
    created_at: datetime

