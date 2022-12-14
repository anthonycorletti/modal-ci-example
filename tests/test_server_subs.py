from uuid import uuid4

from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from hudson.models import Subscription


async def test_create_subscription(
    client: AsyncClient, async_db_session: AsyncSession
) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 200
    subscription = response.json()
    assert subscription["name"] == "default"
    assert subscription["topic"]["id"] == topic["id"]
    assert subscription["topic"]["namespace_id"] == namespace["id"]

    async with async_db_session.begin():
        result = await async_db_session.execute(select(Subscription))
        subs = result.scalars().all()
        assert len(subs) == 1
        assert str(subs[0].topic_id) == topic["id"]


async def test_create_subscription_that_already_exists(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 200
    subscription = response.json()
    assert subscription["name"] == "default"
    assert subscription["topic"]["id"] == topic["id"]
    assert subscription["topic"]["namespace_id"] == namespace["id"]

    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 200
    assert response.json() == subscription


async def test_get_subscriptions(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 200
    subscription = response.json()
    response = await client.get(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions"
    )
    assert response.status_code == 200
    subscriptions = response.json()
    assert len(subscriptions) == 1
    assert subscriptions[0]["name"] == subscription["name"]
    assert subscriptions[0]["topic"]["id"] == subscription["topic"]["id"]
    assert (
        subscriptions[0]["topic"]["namespace_id"]
        == subscription["topic"]["namespace_id"]
    )

    response = await client.get(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions?name=default"
    )
    assert response.status_code == 200
    assert response.json() == subscriptions


async def test_delete_subscription(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 200
    subscription = response.json()
    response = await client.delete(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions/{subscription['id']}"
    )
    assert response.status_code == 200
    response = await client.get(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions"
    )
    assert response.status_code == 200
    subscriptions = response.json()
    assert len(subscriptions) == 0


async def test_create_subscription_missing_namespace_fails(client: AsyncClient) -> None:
    response = await client.post(
        f"/namespaces/{str(uuid4())}/topics/{str(uuid4())}/subscriptions",
        json={
            "name": "default",
            "topic_id": str(uuid4()),
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Namespace not found."


async def test_create_subscription_missing_topic_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{str(uuid4())}/subscriptions",
        json={
            "name": "default",
            "topic_id": str(uuid4()),
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Topic not found."


async def test_get_subscriptions_missing_namespace_fails(client: AsyncClient) -> None:
    response = await client.get(
        f"/namespaces/{str(uuid4())}/topics/{str(uuid4())}/subscriptions"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Namespace not found."


async def test_get_subscriptions_missing_topic_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.get(
        f"/namespaces/{namespace['id']}/topics/{str(uuid4())}/subscriptions"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Topic not found."


async def test_delete_subscription_missing_namespace_fails(client: AsyncClient) -> None:
    response = await client.delete(
        f"/namespaces/{str(uuid4())}/topics/{str(uuid4())}/subscriptions/{str(uuid4())}"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Namespace not found."


async def test_delete_subscription_missing_topic_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.delete(
        f"/namespaces/{namespace['id']}/topics/{str(uuid4())}/subscriptions/{str(uuid4())}"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Topic not found."


async def test_delete_subscription_missing_subscription_fails(
    client: AsyncClient,
) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.delete(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions/{str(uuid4())}"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Subscription not found."


async def test_delete_namespace_cascades_to_subscriptions(
    client: AsyncClient, async_db_session: AsyncSession
) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "https://localhost:4242",
        },
    )
    assert response.status_code == 200
    subscription = response.json()
    response = await client.delete(f"/namespaces/{namespace['id']}")
    assert response.status_code == 200

    async with async_db_session as session:
        assert (
            await session.execute(
                select(Subscription).where(Subscription.id == subscription["id"])
            )
        ).scalar_one_or_none() is None


async def test_create_subscription_needs_https_endpoint(
    client: AsyncClient, async_db_session: AsyncSession
) -> None:
    response = await client.post("/namespaces", json={"name": "hudson"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "http://localhost:4242",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "push_endpoint must be a HTTPS URL"
