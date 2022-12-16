import os
from uuid import uuid4

from httpx import AsyncClient

from hudson._env import env


async def test_create_namespace(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"


async def test_create_namespace_no_duplicates(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    ns_id = response.json()["id"]
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    assert response.json()["id"] == ns_id
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


async def test_get_namespace(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    ns_id = response.json()["id"]
    response = await client.get(f"/namespaces/{ns_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "test"


async def test_get_namespace_not_found(client: AsyncClient) -> None:
    response = await client.get(f"/namespaces/{uuid4()}")
    assert response.status_code == 400


async def test_get_namespaces_q(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    ns_id = response.json()["id"]
    response = await client.get("/namespaces?name=test")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test"
    assert ns_id == response.json()[0]["id"]


async def test_get_namespaces_q_no_match(client: AsyncClient) -> None:
    response = await client.get("/namespaces?name=foo")
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_get_namespaces_q_multiple(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    assert response.json()["name"] == "foo"
    response = await client.get("/namespaces?name=foo")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "foo"


async def test_get_namespaces_q_multiple_no_match(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    assert response.json()["name"] == "foo"
    response = await client.get("/namespaces?name=bar")
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_delete_namespaces(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "foo"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]

    # create a dataset in the namespace
    response = await client.post(
        f"/namespaces/{namespace_id}/datasets",
        json={"name": "foo", "namespace_id": str(namespace_id)},
    )
    assert response.status_code == 200

    response = await client.delete(f"/namespaces/{namespace_id}")
    assert response.status_code == 200

    response = await client.get("/namespaces")
    assert response.status_code == 200
    assert len(response.json()) == 0

    # assert that the namespace directory is gone
    assert not os.path.exists(f"{env.DATASETS_PATH}/{namespace_id}")


async def test_delete_namespace_not_found(client: AsyncClient) -> None:
    response = await client.delete(f"/namespaces/{uuid4()}")
    assert response.status_code == 400
    assert response.status_code == 400
