import json
from datetime import datetime, timezone

# Import the select function and Session class from the SQLAlchemy library, which are used for constructing SQL queries and managing database sessions, respectively.
from sqlalchemy import select
from sqlalchemy.orm import Session

# Import the IncidentModel and IncidentAnalysisModel classes from the app.models.incident and app.models.incident_analysis modules, respectively. These classes represent the database models for incidents and incident analyses, and they are used within the IncidentService class to interact with the database.
from app.models.incident import Incident as IncidentModel
from app.models.incident_analysis import IncidentAnalysis as IncidentAnalysisModel


# Import the IncidentAnalysisResponse, IncidentCreate, and KnowledgeSource Pydantic models from the app.schemas.incident module. These models are used for data validation and serialization when creating incidents and analyzing incident data.
from app.schemas.incident import (
    IncidentAnalysisResponse,
    IncidentCreate,
    KnowledgeSource,
)

# Define the IncidentService class, which provides methods for creating and retrieving incidents from the database. This service class encapsulates the business logic related to incidents and interacts with the database using SQLAlchemy sessions.
from app.ai.analyzer import (
    IncidentAnalysis,
    analyze_incident as run_ai_analysis,
)

# Import the knowledge_search_service instance from the knowledge_search_service module, which provides methods for searching the knowledge base for relevant documents based on a query. This service is used within the IncidentService class to perform knowledge searches related to incidents.
from app.services.knowledge_search_service import knowledge_search_service

# Define the IncidentService class, which provides methods for creating and retrieving incidents from the database. This service class encapsulates the business logic related to incidents and interacts with the database using SQLAlchemy sessions.
from app.services.knowledge_service import knowledge_service

# Import the AIServiceError exception class from the app.core.exceptions module, which is raised when the AI service cannot complete an analysis. This exception is used within the IncidentService class to handle errors related to AI analysis.
from app.core.exceptions import AIServiceError



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

    # Define the get_incident method, which retrieves a specific incident from the database based on its ID. 
    # It takes a SQLAlchemy session and an incident ID as input, executes a SELECT statement to fetch the incident 
    # with the specified ID, and returns the corresponding IncidentModel instance or None if not found.
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


    # Define the analyze_incident method, which performs analysis on a specific incident. 
    # It takes a SQLAlchemy session and an incident ID as input, retrieves the incident from the database, 
    # constructs a dictionary of incident data, calls the analyze_incident function to perform the analysis, 
    # creates an IncidentAnalysisModel instance with the analysis results, adds it to the session, 
    # commits the transaction, and returns the created IncidentAnalysisModel instance.
    def analyze_incident(
        self,
        db: Session,
        incident_id: int,
    ) -> IncidentAnalysisResponse:    
        incident = self.get_incident(db, incident_id)

        if incident is None:
            raise ValueError("Incident not found")


        # Construct a dictionary of incident data to be passed to the AI analysis function.
        incident_data = {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "service": incident.service,
            "description": incident.description,
            "created_at": incident.created_at.isoformat(),
        }


        # Perform a knowledge search based on the incident description to retrieve relevant knowledge documents.
        knowledge_context_documents = knowledge_service.search_knowledge(
            db,
            incident_data["description"],
            limit=3,
        )

        knowledge_context = [
            result.document.content
            for result in knowledge_context_documents
        ]


        # Call the analyze_incident function to perform AI analysis on the incident data, passing in the knowledge context if available.
        try:
            analysis = run_ai_analysis(
                incident_data,
                knowledge_context=knowledge_context,
            )

            # Create a list of KnowledgeSource instances based on the knowledge documents used in the analysis. Each KnowledgeSource instance contains information about the document, such as its ID, title, source, document type, and chunk index.
            knowledge_sources = [
                KnowledgeSource(
                    id=result.document.id,
                    title=result.document.title,
                    source=result.document.source,
                    document_type=result.document.document_type,
                    chunk_index=result.document.chunk_index,
                    similarity_score=1.0 - result.distance,
                )
                for result in knowledge_context_documents
            ]

            
        # Handle any exceptions that occur during the AI analysis process. If an exception is raised, print the error message and raise an AIServiceError to indicate that the AI service could not complete the analysis.
        except Exception as exc:
            raise AIServiceError() from exc

        
        # Create an instance of the IncidentAnalysisModel class to store the analysis results in the database.
        analysis_model = IncidentAnalysisModel(
            incident_id=incident.id,
            summary=analysis.summary,
            probable_cause=analysis.probable_cause,
            impact=analysis.impact,
            recommended_actions=json.dumps(
                analysis.recommended_actions
            ),
            created_at=datetime.now(timezone.utc),
        )

        db.add(analysis_model)
        db.commit()
        db.refresh(analysis_model)

        return IncidentAnalysisResponse(
            summary=analysis.summary,
            probable_cause=analysis.probable_cause,
            impact=analysis.impact,
            recommended_actions=analysis.recommended_actions,
            knowledge_sources=knowledge_sources,
            )
    

# Define an instance of the IncidentService class, which can be used throughout the application to manage incidents. 
# This instance provides access to the methods for creating and retrieving incidents from the database.
incident_service = IncidentService()