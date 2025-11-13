from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from incident_api.models import IncidentSource, IncidentStatus


class IncidentCreate(BaseModel):
    description: str = Field(min_length=1, max_length=5000, examples=["Самокат #1042 не выходит на связь"])
    source: IncidentSource


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus
    resolution: str | None = Field(default=None, max_length=2000, examples=["Перезагружен IoT-модуль"])


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    source: IncidentSource
    status: IncidentStatus
    resolution: str | None
    created_at: datetime
    updated_at: datetime


class IncidentPage(BaseModel):
    items: list[IncidentRead]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    detail: str
