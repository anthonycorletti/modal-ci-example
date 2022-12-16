import base64
import json
from uuid import uuid4

from httpx import AsyncClient


async def test_publish_message_push(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
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
            "push_endpoint": "https://example.com/default",
        },
    )
    assert response.status_code == 200

    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/subscriptions",
        json={
            "name": "default2",
            "topic_id": topic["id"],
            "delivery_type": "push",
            "push_endpoint": "https://example.com/default2",
        },
    )
    assert response.status_code == 200

    data = base64.b64encode(
        json.dumps({"message": "Hello world!"}).encode("utf-8")
    ).decode("utf-8")
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/publish",
        json={"data": data},
    )
    assert response.status_code == 200


async def test_publish_message_missing_namespace_fails(
    client: AsyncClient,
) -> None:
    response = await client.post(
        f"/namespaces/{uuid4()}/topics/{uuid4()}/publish",
        json={"data": "eyJtc2ciOiJoZWxsbyB3b3JsZCEifQo="},
    )
    assert response.status_code == 400


async def test_publish_missing_topic_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{uuid4()}/publish",
        json={"data": "eyJtc2ciOiJoZWxsbyB3b3JsZCEifQo="},
    )
    assert response.status_code == 400


async def test_publish_message_too_big_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/publish",
        json={
            "data": base64.b64encode(("A" * 10_000_000).encode("utf8")).decode("utf8")
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "data"],
                "msg": "Message data must be less than or equal to 10MB.",
                "type": "value_error",
            }
        ]
    }


async def test_publish_message_invalid_b64_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    topic = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/topics/{topic['id']}/publish",
        json={"data": "eyJpbnZhbGlkIjogImpzbw=="},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "data"],
                "msg": "Message data must be a valid base64 encoded JSON string.",
                "type": "value_error",
            }
        ]
    }
