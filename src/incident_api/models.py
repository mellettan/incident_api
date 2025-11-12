import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from incident_api.db import Base


class IncidentStatus(enum.StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentSource(enum.StrEnum):
    OPERATOR = "operator"
    MONITORING = "monitoring"
    PARTNER = "partner"


ALLOWED_TRANSITIONS: dict[IncidentStatus, frozenset[IncidentStatus]] = {
    IncidentStatus.NEW: frozenset({IncidentStatus.IN_PROGRESS, IncidentStatus.RESOLVED, IncidentStatus.CLOSED}),
    IncidentStatus.IN_PROGRESS: frozenset({IncidentStatus.RESOLVED, IncidentStatus.CLOSED}),
    IncidentStatus.RESOLVED: frozenset({IncidentStatus.IN_PROGRESS, IncidentStatus.CLOSED}),
    IncidentStatus.CLOSED: frozenset(),
}


def _enum(enum_class: type[enum.Enum], name: str) -> Enum:
    return Enum(enum_class, name=name, values_callable=lambda members: [member.value for member in members])


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (Index("ix_incidents_status_created_at", "status", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[IncidentSource] = mapped_column(_enum(IncidentSource, "incident_source"))
    status: Mapped[IncidentStatus] = mapped_column(
        _enum(IncidentStatus, "incident_status"), default=IncidentStatus.NEW, server_default=IncidentStatus.NEW.value
    )
    resolution: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def can_transition_to(self, status: IncidentStatus) -> bool:
        """Разрешён ли переход в `status` из текущего статуса."""
        return status in ALLOWED_TRANSITIONS[self.status]
