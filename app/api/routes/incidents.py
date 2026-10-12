from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.incident import Incident, IncidentCreate
from app.services.incident_service import incident_service

# Import the IncidentAnalysis class from the app.ai.analyzer module. This class is used for analyzing incidents and providing insights based on the incident data.
from app.ai.analyzer import IncidentAnalysis

# Import the knowledge_service from the app.services.knowledge_service module. This service is used for managing and retrieving knowledge related to incidents.
from app.services.knowledge_service import knowledge_service



# Router for incident-related endpoints
router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)

# Endpoint to create a new incident
@router.post(
    "",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
):
    return incident_service.create_incident(
        db,
        incident_data,
    )

# Endpoint to retrieve all incidents
@router.get(
    "",
    response_model=list[Incident],
)
def get_incidents(
    db: Session = Depends(get_db),
):
    return incident_service.get_incidents(db)

# Endpoint to retrieve a specific incident by its ID
@router.get(
    "/{incident_id}",
    response_model=Incident,
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = incident_service.get_incident(
        db,
        incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


# Endpoint to analyze an incident using AI
@router.post(
    "/{incident_id}/analyze",
    response_model=IncidentAnalysis,
)
def analyze_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    try:
        return incident_service.analyze_incident(
            db,
            incident_id,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )


# Endpoint to ingest knowledge documents (Markdown runbooks) into the database
@router.post("/knowledge/ingest")
def ingest_knowledge(db: Session = Depends(get_db)):
    try:
        inserted_count = knowledge_service.ingest_runbooks(db)
        return {
            "message": "Knowledge ingestion completed",
            "chunks_ingested": inserted_count,
        }
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )