from typing import Annotated, Any

from fastapi import APIRouter, Query, status

from incident_api.api.dependencies import IncidentServiceDep
from incident_api.models import Incident, IncidentSource, IncidentStatus
from incident_api.schemas import ErrorResponse, IncidentCreate, IncidentPage, IncidentRead, IncidentStatusUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=IncidentRead)
async def create_incident(payload: IncidentCreate, service: IncidentServiceDep) -> Incident:
    """Зарегистрировать инцидент. Новый инцидент получает статус `new`."""
    return await service.create(payload.description, payload.source)


@router.get("", response_model=IncidentPage)
async def list_incidents(
    service: IncidentServiceDep,
    status_filter: Annotated[IncidentStatus | None, Query(alias="status")] = None,
    source: IncidentSource | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> IncidentPage:
    """Список инцидентов от новых к старым с фильтрами по статусу и источнику."""
    items, total = await service.list(status_filter, source, limit, offset)
    return IncidentPage(
        items=[IncidentRead.model_validate(item) for item in items], total=total, limit=limit, offset=offset
    )


@router.get("/{incident_id}", response_model=IncidentRead, responses=NOT_FOUND)
async def get_incident(incident_id: int, service: IncidentServiceDep) -> Incident:
    return await service.get(incident_id)


@router.patch(
    "/{incident_id}",
    response_model=IncidentRead,
    responses={**NOT_FOUND, status.HTTP_409_CONFLICT: {"model": ErrorResponse}},
)
async def update_incident_status(
    incident_id: int, payload: IncidentStatusUpdate, service: IncidentServiceDep
) -> Incident:
    """Сменить статус. Допустимые переходы: new → in_progress | resolved | closed,
    in_progress → resolved | closed, resolved → in_progress | closed; closed — финальный."""
    return await service.change_status(incident_id, payload.status, payload.resolution)
