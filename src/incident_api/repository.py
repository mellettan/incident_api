from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from incident_api.models import Incident, IncidentSource, IncidentStatus


class IncidentRepository:
    """Доступ к таблице инцидентов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, incident: Incident) -> Incident:
        self._session.add(incident)
        await self._session.flush()
        await self._session.refresh(incident)
        return incident

    async def get(self, incident_id: int, for_update: bool = False) -> Incident | None:
        query = select(Incident).where(Incident.id == incident_id)
        if for_update:
            query = query.with_for_update()
        incident: Incident | None = await self._session.scalar(query)
        return incident

    async def list(
        self,
        status: IncidentStatus | None,
        source: IncidentSource | None,
        limit: int,
        offset: int,
    ) -> tuple[Sequence[Incident], int]:
        filters = []
        if status is not None:
            filters.append(Incident.status == status)
        if source is not None:
            filters.append(Incident.source == source)
        total = await self._session.scalar(select(func.count()).select_from(Incident).where(*filters))
        items = await self._session.scalars(
            select(Incident)
            .where(*filters)
            .order_by(Incident.created_at.desc(), Incident.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return items.all(), total or 0

    async def save(self, incident: Incident) -> Incident:
        await self._session.flush()
        await self._session.refresh(incident)
        return incident
