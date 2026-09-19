from fastapi import APIRouter, HTTPException, status

from app.schemas.incident import Incident, IncidentCreate
from app.services.incident_service import incident_service


# Define an API router for managing incidents, which includes endpoints for creating, retrieving, and deleting incidents.
router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)

# Define an endpoint for creating a new incident, which takes an IncidentCreate object as input and returns the created Incident object. The endpoint is decorated with the @router.post decorator, which specifies the HTTP method (POST), the response model (Incident), and the status code (201 Created).
@router.post(
    "/",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
    )

# Define an endpoint for retrieving all incidents, which returns a list of Incident objects. The endpoint is decorated with the @router.get decorator, which specifies the HTTP method (GET) and the response model (list[Incident]).
def create_incident(incident_data: IncidentCreate):
    return incident_service.create_incident(incident_data)


# Define an endpoint for retrieving all incidents, which returns a list of Incident objects. The endpoint is decorated with the @router.get decorator, which specifies the HTTP method (GET) and the response model (list[Incident]).
@router.get(
    "/",
    response_model=list[Incident],
)
# Define an endpoint for retrieving all incidents, which returns a list of Incident objects. The endpoint is decorated with the @router.get decorator, which specifies the HTTP method (GET) and the response model (list[Incident]).
def get_incidents():
    return incident_service.get_incident()


# Define an endpoint for retrieving a specific incident by its ID, which returns an Incident object. The endpoint is decorated with the @router.get decorator, which specifies the HTTP method (GET), the response model (Incident), and the path parameter (incident_id).
@router.get(
    "/{incident_id}",
    response_model=Incident,
)
# Define an endpoint for retrieving a specific incident by its ID, which returns an Incident object. The endpoint is decorated with the @router.get decorator, which specifies the HTTP method (GET), the response model (Incident), and the path parameter (incident_id).
def get_incident(incident_id: int):
    incident = incident_service.get_incident(incident_id) # type: ignore

    # If the incident is not found, raise an HTTPException with a 404 status code and a message indicating that the incident was not found. Otherwise, return the incident object.
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )
    return incident


# Define an endpoint for deleting a specific incident by its ID, which returns a 204 No Content status code if the deletion is successful. The endpoint is decorated with the @router.delete decorator, which specifies the HTTP method (DELETE), the path parameter (incident_id), and the status code (204 No Content).
@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)

# Define an endpoint for deleting a specific incident by its ID, which returns a 204 No Content status code if the deletion is successful. The endpoint is decorated with the @router.delete decorator, which specifies the HTTP method (DELETE), the path parameter (incident_id), and the status code (204 No Content).
def delete_incident(incident_id: int):
    deleted = incident_service.delete_incident(incident_id)

    # If the incident is not found, raise an HTTPException with a 404 status code and a message indicating that the incident was not found. Otherwise, return a 204 No Content status code.
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )

    