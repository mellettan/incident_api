import pytest
import pytest_asyncio
from databases import Database
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport  # noqa - pytest так требует))

from src.core.config import settings
from src.main import app
from src.core.db import engine, metadata


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    """Создаём таблицы в тестовой БД перед запуском тестов"""
    database = Database(settings.DATABASE_TESTS_URL)
    await database.connect()
    metadata.create_all(bind=engine)
    yield
    metadata.drop_all(bind=engine)
    await database.disconnect()


@pytest_asyncio.fixture
async def test_app():
    """Асинхронный HTTP-клиент для тестов"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_create_incident(test_app):
    payload = {"description": "Самокат не в сети", "source": "monitoring"}
    response = await test_app.post("/incidents/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == payload["description"]
    assert data["source"] == payload["source"]
    assert data["status"] == "new"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_incidents(test_app):
    await test_app.post(
        "/incidents/", json={"description": "Ошибка API", "source": "operator"}
    )
    await test_app.post(
        "/incidents/",
        json={"description": "Сервер не отвечает", "source": "monitoring"},
    )

    response = await test_app.get("/incidents/")
    assert response.status_code == 200
    incidents = response.json()
    assert isinstance(incidents, list)
    assert len(incidents) >= 2


@pytest.mark.asyncio
async def test_list_incidents_with_status(test_app):
    # создаём инциденты с разными статусами
    await test_app.post("/incidents/", json={"description": "Инцидент A", "source": "monitoring"})
    resp = await test_app.post("/incidents/", json={"description": "Инцидент B", "source": "operator"})
    incident_b_id = resp.json()["id"]

    # обновим статус B
    await test_app.patch(f"/incidents/{incident_b_id}", json={"status": "resolved"})

    # запрос только с фильтром status=resolved
    response = await test_app.get("/incidents/", params={"status": "resolved"})
    assert response.status_code == 200
    incidents = response.json()
    assert all(i["status"] == "resolved" for i in incidents)



@pytest.mark.asyncio
async def test_update_status(test_app):
    resp = await test_app.post(
        "/incidents/", json={"description": "Тест обновления", "source": "operator"}
    )
    incident_id = resp.json()["id"]

    response = await test_app.patch(
        f"/incidents/{incident_id}", json={"status": "resolved"}
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "resolved"


@pytest.mark.asyncio
async def test_update_status_not_found(test_app):
    response = await test_app.patch("/incidents/9999", json={"status": "resolved"})
    assert response.status_code == 404
