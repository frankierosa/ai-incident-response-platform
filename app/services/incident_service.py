from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident as IncidentModel
from app.schemas.incident import Incident as IncidentSchema
from app.schemas.incident import IncidentCreate


class IncidentService:

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

    def get_incidents(
        self,
        db: Session,
    ) -> list[IncidentModel]:

        statement = select(IncidentModel)

        result = db.execute(statement)

        return list(result.scalars().all())

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


incident_service = IncidentService()