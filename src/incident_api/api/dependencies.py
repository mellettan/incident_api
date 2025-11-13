from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from incident_api.db import session_scope
from incident_api.repository import IncidentRepository
from incident_api.service import IncidentService


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async for session in session_scope(request.app.state.sessionmaker):
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_incident_service(session: SessionDep) -> IncidentService:
    return IncidentService(IncidentRepository(session))


IncidentServiceDep = Annotated[IncidentService, Depends(get_incident_service)]
