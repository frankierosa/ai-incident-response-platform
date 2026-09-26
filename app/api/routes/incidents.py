from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.incident import Incident, IncidentCreate
from app.services.incident_service import incident_service


router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)


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


@router.get(
    "",
    response_model=list[Incident],
)
def get_incidents(
    db: Session = Depends(get_db),
):
    return incident_service.get_incidents(db)


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