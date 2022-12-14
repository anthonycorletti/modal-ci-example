from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession


async def test_create_topics(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]
    response = await client.post(
        f"/namespaces/{namespace_id}/topics",
        json={"name": "test", "namespace_id": namespace_id},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    assert response.json()["namespace"]["id"] == namespace_id
    assert response.json()["id"] is not None
    assert response.json()["created_at"] is not None


async def test_get_topics(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]
    response = await client.post(
        f"/namespaces/{namespace_id}/topics",
        json={"name": "test", "namespace_id": namespace_id},
    )
    assert response.status_code == 200
    topic_id = response.json()["id"]
    response = await client.get(f"/namespaces/{namespace_id}/topics")
    assert response.status_code == 200
    assert response.json()[0]["id"] == topic_id
    assert response.json()[0]["name"] == "test"
    assert response.json()[0]["namespace"]["id"] == namespace_id


async def test_delete_topics(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]
    response = await client.post(
        f"/namespaces/{namespace_id}/topics",
        json={"name": "test", "namespace_id": namespace_id},
    )
    assert response.status_code == 200
    topic_id = response.json()["id"]
    response = await client.delete(f"/namespaces/{namespace_id}/topics/{topic_id}")
    assert response.status_code == 200
    assert response.json()["id"] == topic_id
    assert response.json()["name"] == "test"
    assert response.json()["namespace"]["id"] == namespace_id
    response = await client.get(f"/namespaces/{namespace_id}/topics")
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_delete_namespace_cascades_topics(
    client: AsyncClient, async_db_session: AsyncSession
) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]
    response = await client.post(
        f"/namespaces/{namespace_id}/topics",
        json={"name": "test", "namespace_id": namespace_id},
    )
    assert response.status_code == 200

    async with async_db_session.begin():
        result = await async_db_session.execute(text("SELECT * FROM topics"))
        assert len(result.scalars().all()) == 1

    response = await client.delete(f"/namespaces/{namespace_id}")
    assert response.status_code == 200
    assert response.json()["id"] == namespace_id
    assert response.json()["name"] == "test"

    async with async_db_session.begin():
        result = await async_db_session.execute(text("SELECT * FROM topics"))
        assert result.scalars().all() == []


async def test_get_topic_with_query(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]
    response = await client.post(
        f"/namespaces/{namespace_id}/topics",
        json={"name": "test", "namespace_id": namespace_id},
    )
    assert response.status_code == 200
    topic_id = response.json()["id"]
    response = await client.get(f"/namespaces/{namespace_id}/topics?name=tes")
    assert response.status_code == 200
    assert response.json()[0]["id"] == topic_id
    assert response.json()[0]["name"] == "test"
    assert response.json()[0]["namespace"]["id"] == namespace_id


async def test_create_topic_already_exists(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]

    response = await client.post(
        f"/namespaces/{namespace_id}/topics",
        json={"name": "test", "namespace_id": namespace_id},
    )
    assert response.status_code == 200
    topic_id = response.json()["id"]

    response = await client.post(
        f"/namespaces/{namespace_id}/topics",
        json={"name": "test", "namespace_id": namespace_id},
    )
    assert response.status_code == 200
    assert response.json()["id"] == topic_id

    # assert there is one topic
    response = await client.get(f"/namespaces/{namespace_id}/topics")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_topics_missing_namespace_fails(client: AsyncClient) -> None:
    response = await client.get(f"/namespaces/{uuid4()}/topics")
    assert response.status_code == 400
    assert response.json()["detail"] == "Namespace not found."


async def test_create_topic_missing_namespace_fails(client: AsyncClient) -> None:
    ns_id = str(uuid4())
    response = await client.post(
        f"/namespaces/{ns_id}/topics", json={"name": "test", "namespace_id": ns_id}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Namespace not found."


async def test_delete_topic_missing_namespace_fails(client: AsyncClient) -> None:
    response = await client.delete(f"/namespaces/{uuid4()}/topics/{uuid4()}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Namespace not found."


async def test_delete_topic_not_found_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "test"})
    assert response.status_code == 200
    namespace_id = response.json()["id"]
    response = await client.delete(f"/namespaces/{namespace_id}/topics/{uuid4()}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Topic not found."
