from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident as IncidentModel
from app.schemas.incident import IncidentCreate

from app.ai.analyzer import analyze_incident
from app.ai.analyzer import IncidentAnalysis

# Define the IncidentService class, which provides methods for creating and retrieving incidents from the database. This service class encapsulates the business logic related to incidents and interacts with the database using SQLAlchemy sessions.  
class IncidentService:

    # Define the create_incident method, which creates a new incident in the database. It takes a SQLAlchemy session and an IncidentCreate schema as input, constructs an Incident model instance, adds it to the session, commits the transaction, and returns the created incident.
    def create_incident(
        self,
        db: Session,
        incident_data: IncidentCreate,
    ) -> IncidentModel:

        incident = IncidentModel(
            title=incident_data.title,
            severity=incident_data.severity.value,
            status=incident_data.status.value,
            service=incident_data.service,
            description=incident_data.description,
            created_at=datetime.now(timezone.utc),
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident

    # Define the get_incidents method, which retrieves all incidents from the database. It takes a SQLAlchemy session as input, executes a SELECT statement to fetch all incidents, and returns a list of IncidentModel instances.
    def get_incidents(
        self,
        db: Session,
    ) -> list[IncidentModel]:

        statement = select(IncidentModel)

        result = db.execute(statement)

        return list(result.scalars().all())

    # Define the get_incident method, which retrieves a specific incident from the database based on its ID. It takes a SQLAlchemy session and an incident ID as input, executes a SELECT statement to fetch the incident with the specified ID, and returns the corresponding IncidentModel instance or None if not found.
    def get_incident(
        self,
        db: Session,
        incident_id: int,
    ) -> IncidentModel | None:

        statement = select(IncidentModel).where(
            IncidentModel.id == incident_id
        )

        result = db.execute(statement)

        return result.scalar_one_or_none()


    # Define the analyze_incident method, which analyzes a specific incident using the AI analyzer. It takes a SQLAlchemy session and an incident ID as input, retrieves the incident from the database, constructs a dictionary with the incident's data, and invokes the analyze_incident function from the AI analyzer module to perform the analysis. The method returns an IncidentAnalysis instance containing the analysis results.
    def analyze_incident(
        self,
        db: Session,
        incident_id: int,
    ) -> IncidentAnalysis:
        incident = self.get_incident(db, incident_id)

        if incident is None:
            raise ValueError("Incident not found")

        incident_data = {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "service": incident.service,
            "description": incident.description,
            "created_at": incident.created_at.isoformat(),
        }

        return analyze_incident(incident_data)
    

# Define an instance of the IncidentService class, which can be used throughout the application to manage incidents. This instance provides access to the methods for creating and retrieving incidents from the database.
incident_service = IncidentService()