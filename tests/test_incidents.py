import asyncio

import pytest
from httpx import AsyncClient


async def create(client: AsyncClient, description: str = "Самокат не в сети", source: str = "monitoring") -> dict:
    response = await client.post("/incidents", json={"description": description, "source": source})
    assert response.status_code == 201, response.text
    return response.json()


async def set_status(client: AsyncClient, incident_id: int, status: str, **extra) -> tuple[int, dict]:
    response = await client.patch(f"/incidents/{incident_id}", json={"status": status, **extra})
    return response.status_code, response.json()


async def test_create_incident(client: AsyncClient):
    incident = await create(client, "Точка не отвечает", "operator")

    assert incident["id"] == 1
    assert incident["description"] == "Точка не отвечает"
    assert incident["source"] == "operator"
    assert incident["status"] == "new"
    assert incident["resolution"] is None
    assert incident["created_at"] == incident["updated_at"]


@pytest.mark.parametrize(
    "payload",
    [
        {"description": "", "source": "operator"},
        {"description": "ok", "source": "telegram"},
        {"source": "operator"},
    ],
)
async def test_create_validation(client: AsyncClient, payload: dict):
    response = await client.post("/incidents", json=payload)

    assert response.status_code == 422


async def test_get_incident(client: AsyncClient):
    incident = await create(client)

    response = await client.get(f"/incidents/{incident['id']}")
    missing = await client.get("/incidents/999")

    assert response.json() == incident
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Инцидент 999 не найден"}


async def test_list_is_sorted_and_paginated(client: AsyncClient):
    for index in range(5):
        await create(client, f"Инцидент {index}")

    first_page = (await client.get("/incidents", params={"limit": 2})).json()
    last_page = (await client.get("/incidents", params={"limit": 2, "offset": 4})).json()

    assert first_page["total"] == 5
    assert [item["description"] for item in first_page["items"]] == ["Инцидент 4", "Инцидент 3"]
    assert [item["description"] for item in last_page["items"]] == ["Инцидент 0"]


async def test_list_filters(client: AsyncClient):
    a = await create(client, "A", "operator")
    await create(client, "B", "monitoring")
    c = await create(client, "C", "partner")
    await set_status(client, a["id"], "in_progress")
    await set_status(client, c["id"], "in_progress")

    in_progress = (await client.get("/incidents", params={"status": "in_progress"})).json()
    partner_in_progress = (await client.get("/incidents", params={"status": "in_progress", "source": "partner"})).json()

    assert {item["description"] for item in in_progress["items"]} == {"A", "C"}
    assert [item["description"] for item in partner_in_progress["items"]] == ["C"]
    assert partner_in_progress["total"] == 1


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 201}, {"offset": -1}, {"status": "unknown"}])
async def test_list_rejects_bad_params(client: AsyncClient, params: dict):
    assert (await client.get("/incidents", params=params)).status_code == 422


async def test_status_lifecycle(client: AsyncClient):
    incident = await create(client)

    code, taken = await set_status(client, incident["id"], "in_progress")
    assert code == 200
    assert taken["status"] == "in_progress"
    assert taken["updated_at"] > incident["updated_at"]

    code, resolved = await set_status(client, incident["id"], "resolved", resolution="Перезагрузили модуль")
    assert code == 200
    assert resolved["resolution"] == "Перезагрузили модуль"

    code, closed = await set_status(client, incident["id"], "closed")
    assert code == 200
    assert closed["status"] == "closed"


async def test_closed_incident_cannot_be_reopened(client: AsyncClient):
    incident = await create(client)
    await set_status(client, incident["id"], "closed")

    code, body = await set_status(client, incident["id"], "in_progress")

    assert code == 409
    assert body == {"detail": "Нельзя перевести инцидент из статуса closed в in_progress"}


async def test_same_status_is_idempotent(client: AsyncClient):
    incident = await create(client)

    code, body = await set_status(client, incident["id"], "new")

    assert code == 200
    assert body["updated_at"] == incident["updated_at"]


async def test_update_missing_incident(client: AsyncClient):
    code, _ = await set_status(client, 404, "closed")

    assert code == 404


async def test_concurrent_updates_respect_transitions(client: AsyncClient):
    incident = await create(client)
    await set_status(client, incident["id"], "resolved")

    results = await asyncio.gather(
        set_status(client, incident["id"], "closed"),
        set_status(client, incident["id"], "in_progress"),
    )

    codes = sorted(code for code, _ in results)
    final = (await client.get(f"/incidents/{incident['id']}")).json()
    assert codes in ([200, 200], [200, 409])
    if codes == [200, 409]:
        assert final["status"] == "closed"


async def test_health(client: AsyncClient):
    response = await client.get("/health")

    assert response.json() == {"status": "ok"}
