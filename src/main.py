from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api import incidents
from src.core.db import database


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(
    title="Incident API",
    lifespan=lifespan,
)

app.include_router(incidents.router)


