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



# Define the Incident Pydantic model, which extends the IncidentCreate model and adds additional fields for id and created_at. The model_config is set to allow attribute-based access to the model's fields.
class Incident(IncidentCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# Define the KnowledgeSource Pydantic model, which represents a reference to knowledge used during incident analysis. It includes fields for id, title, source, document_type, and chunk_index, with attribute-based access enabled in the model_config.
class KnowledgeSource(BaseModel):
    """Reference to knowledge used during incident analysis."""

    id: int
    title: str
    source: str
    document_type: str
    chunk_index: int

    model_config = {
        "from_attributes": True
    }

# Define the IncidentAnalysisResponse Pydantic model, which represents the response of an AI incident analysis. It includes fields for summary, probable_cause, impact, recommended_actions, and knowledge_sources, which is a list of KnowledgeSource objects.
class IncidentAnalysisResponse(BaseModel):
    """AI incident analysis together with the knowledge used to produce it."""

    summary: str
    probable_cause: str
    impact: str
    recommended_actions: list[str]
    knowledge_sources: list[KnowledgeSource]