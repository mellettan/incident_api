import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class IncidentStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class IncidentCreate(BaseModel):
    description: str
    source: str


class IncidentUpdate(BaseModel):
    status: IncidentStatus


class IncidentOut(BaseModel):
    id: int
    description: str
    status: IncidentStatus
    source: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
