from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# This model represents the analysis of an incident, including its summary, 
# probable cause, impact, and recommended actions. It is linked to the Incident model via a foreign key relationship.
class IncidentAnalysis(Base):
    __tablename__ = "incident_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    probable_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    impact: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    recommended_actions: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="analysis",
    )