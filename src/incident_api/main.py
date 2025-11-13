import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import async_sessionmaker

from incident_api.api import health, incidents
from incident_api.config import Settings, get_settings
from incident_api.db import create_engine
from incident_api.service import IncidentNotFoundError, InvalidStatusTransitionError


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_engine(settings)
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        yield
        await engine.dispose()

    app = FastAPI(title="Incident API", version="1.0.0", lifespan=lifespan)
    app.include_router(incidents.router)
    app.include_router(health.router)

    @app.exception_handler(IncidentNotFoundError)
    async def not_found(_: Request, exc: IncidentNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(InvalidStatusTransitionError)
    async def conflict(_: Request, exc: InvalidStatusTransitionError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

    return app
