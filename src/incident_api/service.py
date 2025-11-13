from collections.abc import Sequence

from incident_api.models import Incident, IncidentSource, IncidentStatus
from incident_api.repository import IncidentRepository


class IncidentNotFoundError(LookupError):
    def __init__(self, incident_id: int) -> None:
        super().__init__(f"Инцидент {incident_id} не найден")


class InvalidStatusTransitionError(ValueError):
    def __init__(self, current: IncidentStatus, target: IncidentStatus) -> None:
        super().__init__(f"Нельзя перевести инцидент из статуса {current.value} в {target.value}")


class IncidentService:
    """Бизнес-логика инцидентов: создание, поиск и смена статуса по правилам."""

    def __init__(self, repository: IncidentRepository) -> None:
        self._repository = repository

    async def create(self, description: str, source: IncidentSource) -> Incident:
        return await self._repository.add(Incident(description=description, source=source))

    async def get(self, incident_id: int) -> Incident:
        incident = await self._repository.get(incident_id)
        if incident is None:
            raise IncidentNotFoundError(incident_id)
        return incident

    async def list(
        self,
        status: IncidentStatus | None = None,
        source: IncidentSource | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[Incident], int]:
        return await self._repository.list(status, source, limit, offset)

    async def change_status(self, incident_id: int, status: IncidentStatus, resolution: str | None = None) -> Incident:
        """Меняет статус под блокировкой строки, чтобы параллельные запросы не обошли правила переходов."""
        incident = await self._repository.get(incident_id, for_update=True)
        if incident is None:
            raise IncidentNotFoundError(incident_id)
        if incident.status == status:
            return incident
        if not incident.can_transition_to(status):
            raise InvalidStatusTransitionError(incident.status, status)
        incident.status = status
        if resolution is not None:
            incident.resolution = resolution
        return await self._repository.save(incident)
