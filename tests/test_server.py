import os

from fastapi.testclient import TestClient

from hudson import __version__


async def test_tz() -> None:
    assert os.environ["TZ"] == "UTC"


async def test_healthcheck(client: TestClient) -> None:
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json()["message"] == "⛵️"
    assert response.json()["version"] == __version__


async def test_create_namespace(client: TestClient) -> None:
    response = client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"


async def test_get_namespaces(client: TestClient) -> None:
    response = client.get("/namespaces")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test"


async def test_get_namespaces_q(client: TestClient) -> None:
    response = client.get("/namespaces?q=test")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test"


async def test_get_namespaces_q_no_match(client: TestClient) -> None:
    response = client.get("/namespaces?q=foo")
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_get_namespaces_q_multiple(client: TestClient) -> None:
    response = client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    assert response.json()["name"] == "foo"
    response = client.get("/namespaces?q=foo")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "foo"


async def test_get_namespaces_q_multiple_no_match(client: TestClient) -> None:
    response = client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    assert response.json()["name"] == "foo"
    response = client.get("/namespaces?q=bar")
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_delete_namespaces(client: TestClient) -> None:
    response = client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]

    response = client.delete(f"/namespaces/{namespace_id}")
    assert response.status_code == 200
    response = client.get("/namespaces")
    assert response.status_code == 200
    assert len(response.json()) == 1
