from datetime import datetime, timezone
from app.schemas.incident import Incident, IncidentCreate


# Define a service class for managing incidents, which includes methods for creating incidents and storing them in an in-memory dictionary.
class IncidentService:

    # Initialize the IncidentService with an empty dictionary to store incidents and a counter for generating unique incident IDs.
    def __init__(self):
        # Initialize an empty list to store incidents and a counter for generating unique incident IDs.
        self._incidents: dict[int, Incident] = {}
        self._next_id: int = 1001

    # Define a method for creating a new incident, which takes an IncidentCreate object as input and returns an Incident object.
    def create_incident(self, incident_data: IncidentCreate) -> Incident:
        # Create a new incident with a unique ID and the current timestamp, then store it in the incidents dictionary.
        incident = Incident(
            id=self._next_id,
            created_at=datetime.now(timezone.utc),
            **incident_data.model_dump(),
        )
        self._incidents[self._next_id] = incident
        self._next_id += 1

        return incident

    # Define a method for retrieving all incidents, which returns a list of Incident objects.
    def get_incident(self) -> list[Incident]:
        # Return a list of all incidents stored in the incidents dictionary.
        return list(self._incidents.values())

    # Define a method for retrieving an incident by its ID, which takes an incident ID as input and returns the corresponding Incident object or None if not found.
    def get_incident_by_id(self, incident_id: int) -> Incident | None:
        # Retrieve an incident by its ID from the incidents dictionary, returning None if not found.
        return self._incidents.get(incident_id)

    # Define a method for deleting an incident by its ID, which takes an incident ID as input and returns a boolean indicating whether the deletion was successful.
    def delete_incident(self, incident_id: int) -> bool:
        # Delete an incident by its ID from the incidents dictionary, returning True if successful or False if not found.
        if incident_id not in self._incidents:
            return False
        
        del self._incidents[incident_id]
        return True


# Create an instance of the IncidentService class to be used for managing incidents in the application.
incident_service = IncidentService()