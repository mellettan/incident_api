import enum
from sqlalchemy import Table, Column, Integer, String, DateTime, Enum, func
from src.core.db import metadata


class IncidentStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


incident = Table(
    "incidents",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("description", String, nullable=False),
    Column("status", Enum(IncidentStatus), nullable=False, default=IncidentStatus.NEW),
    Column("source", String, nullable=False),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
)
