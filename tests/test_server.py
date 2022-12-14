import os

from httpx import AsyncClient

from hudson import __version__


async def test_tz() -> None:
    assert os.environ["TZ"] == "UTC"


async def test_healthcheck(client: AsyncClient) -> None:
    response = await client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json()["message"] == "⛵️"
    assert response.json()["version"] == __version__


async def test_create_namespace(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"


async def test_create_namespace_no_duplicates(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    response = await client.get("/namespaces")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_namespaces(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    response = await client.get("/namespaces")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test"


async def test_get_namespaces_q(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    ns_id = response.json()["id"]
    response = await client.get("/namespaces?q=test")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test"
    assert ns_id == response.json()[0]["id"]


async def test_get_namespaces_q_no_match(client: AsyncClient) -> None:
    response = await client.get("/namespaces?q=foo")
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_get_namespaces_q_multiple(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    assert response.json()["name"] == "foo"
    response = await client.get("/namespaces?q=foo")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "foo"


async def test_get_namespaces_q_multiple_no_match(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    assert response.json()["name"] == "foo"
    response = await client.get("/namespaces?q=bar")
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_delete_namespaces(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]

    response = await client.delete(f"/namespaces/{namespace_id}")
    assert response.status_code == 200

    response = await client.get("/namespaces")
    assert response.status_code == 200
    assert len(response.json()) == 0
