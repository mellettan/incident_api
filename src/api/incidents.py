from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.core.db import database
from src.models.incident import incident
from src.schemas.incident import (
    IncidentCreate,
    IncidentOut,
    IncidentUpdate,
    IncidentStatus,
)
from sqlalchemy import select, update

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("/", response_model=IncidentOut, status_code=201)
async def create_incident(data: IncidentCreate):
    query = incident.insert().values(
        description=data.description,
        source=data.source,
        status=IncidentStatus.new,
    )
    new_id = await database.execute(query)
    row = await database.fetch_one(select(incident).where(incident.c.id == new_id))
    return IncidentOut(**row)


@router.get("/", response_model=List[IncidentOut])
async def list_incidents(status: Optional[IncidentStatus] = Query(None)):
    query = select(incident)
    if status:
        query = query.where(incident.c.status == status)
    rows = await database.fetch_all(query.order_by(incident.c.created_at.desc()))
    return [IncidentOut(**r) for r in rows]


@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_status(incident_id: int, data: IncidentUpdate):
    query = (
        update(incident)
        .where(incident.c.id == incident_id)
        .values(status=data.status)
        .returning(incident)
    )
    row = await database.fetch_one(query)
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentOut(**row)
