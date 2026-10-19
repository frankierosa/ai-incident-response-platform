from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.incident_service import incident_service

from app.schemas.incident import (
    Incident,
    IncidentAnalysisResponse,
    IncidentCreate,
)

# Import the knowledge_service from the app.services.knowledge_service module. This service is used for managing and retrieving knowledge related to incidents.
from app.services.knowledge_service import knowledge_service

# Import the AIServiceError exception from the app.core.exceptions module. This exception is used to handle errors related to AI services in the application.
from app.core.exceptions import AIServiceError




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


# Endpoint to analyze a specific incident using AI
@router.post(
    "/{incident_id}/analyze",
    response_model=IncidentAnalysisResponse,
)


# The analyze_incident function is an endpoint that analyzes a specific incident using AI. It takes the incident ID as a path parameter and a database session as a dependency. The function calls the analyze_incident method from the incident_service to perform the analysis. If the incident is not found, it raises a 404 Not Found HTTP exception. If there is an error with the AI service, it raises a 503 Service Unavailable HTTP exception with a relevant error message.
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

    # Handle AIServiceError exceptions raised during the analysis process. If the AI service is unavailable or encounters an error, return a 503 Service Unavailable response with a relevant error message.
    except AIServiceError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "AI_SERVICE_UNAVAILABLE",
                "message": "AI analysis is temporarily unavailable. Please try again later. Please contact your system administrator if the issue persists.",
            },
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