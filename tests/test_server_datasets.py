import os
from uuid import uuid4

from docarray import Document, DocumentArray
from httpx import AsyncClient

from hudson._env import env


async def test_create_dataset(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    dataset = response.json()
    assert dataset["name"] == "default"
    assert dataset["namespace"]["id"] == namespace["id"]


async def test_create_dataset_with_description(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={
            "name": "default",
            "namespace_id": namespace["id"],
            "description": "test",
        },
    )
    assert response.status_code == 200
    dataset = response.json()
    assert dataset["name"] == "default"
    assert dataset["namespace"]["id"] == namespace["id"]
    assert dataset["description"] == "test"


async def test_get_datasets(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    response = await client.get(f"/namespaces/{namespace['id']}/datasets")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_dataset(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    dataset = response.json()
    response = await client.get(
        f"/namespaces/{namespace['id']}/datasets/{dataset['id']}"
    )
    assert response.status_code == 200
    assert response.json()["name"] == "default"
    assert response.json()["namespace"]["id"] == namespace["id"]


async def test_get_missing_dataset_in_namespace_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.get(f"/namespaces/{namespace['id']}/datasets/{uuid4()}")
    assert response.status_code == 400


async def test_missing_dataset_fails(client: AsyncClient) -> None:
    response = await client.get(f"/namespaces/{uuid4()}/datasets/{uuid4()}")
    assert response.status_code == 400


async def test_get_dataset_name_query(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    dataset = response.json()
    response = await client.get(
        f"/namespaces/{namespace['id']}/datasets?name={dataset['name']}"
    )
    assert response.status_code == 200
    dataset = response.json()[0]
    assert dataset["name"] == "default"
    assert dataset["namespace"]["id"] == namespace["id"]


async def test_create_dataset_missing_namespace_fails(client: AsyncClient) -> None:
    ns_id = str(uuid4())
    response = await client.post(
        f"/namespaces/{ns_id}/datasets",
        json={"name": "default", "namespace_id": ns_id},
    )
    assert response.status_code == 400


async def test_create_dataset_missing_name_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"namespace_id": namespace["id"]},
    )
    assert response.status_code == 422


async def test_no_duplicate_datasets(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    response = await client.get(f"/namespaces/{namespace['id']}/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) == 1


async def test_delete_dataset(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    dataset = response.json()
    response = await client.delete(
        f"/namespaces/{namespace['id']}/datasets/{dataset['id']}"
    )
    assert response.status_code == 200
    response = await client.get(f"/namespaces/{namespace['id']}/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) == 0
    assert not os.path.exists(f"{env.DATASETS_PATH}/{namespace['id']}/{dataset['id']}")


async def test_get_dataset_missing_namespace_fails(client: AsyncClient) -> None:
    ns_id = str(uuid4())
    response = await client.get(f"/namespaces/{ns_id}/datasets")
    assert response.status_code == 400


async def test_delete_dataset_missing_namespace_fails(client: AsyncClient) -> None:
    ns_id = str(uuid4())
    ds_id = str(uuid4())
    response = await client.delete(f"/namespaces/{ns_id}/datasets/{ds_id}")
    assert response.status_code == 400


async def test_delete_missing_dataset_from_namespace_fails(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    ds_id = str(uuid4())
    response = await client.delete(f"/namespaces/{namespace['id']}/datasets/{ds_id}")
    assert response.status_code == 400


async def test_write_to_dataset(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    dataset = response.json()
    da = DocumentArray()
    da.extend([Document(text="hello"), Document(text="world!")])
    _json = {"data": [d.dict() for d in da.to_pydantic_model()]}
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets/{dataset['id']}/write",
        json=_json,
    )
    assert response.status_code == 200
    # count the number of files in the dataset path for this dataset
    dataset_path = f"{env.DATASETS_PATH}/{namespace['id']}/{dataset['id']}"
    assert len(os.listdir(dataset_path)) == 1


async def test_read_from_dataset(client: AsyncClient) -> None:
    response = await client.post("/namespaces", json={"name": "default"})
    assert response.status_code == 200
    namespace = response.json()
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets",
        json={"name": "default", "namespace_id": namespace["id"]},
    )
    assert response.status_code == 200
    dataset = response.json()
    da = DocumentArray()
    da.extend([Document(text="hello"), Document(text="world!")])
    _json = {"data": [d.dict() for d in da.to_pydantic_model()]}
    response = await client.post(
        f"/namespaces/{namespace['id']}/datasets/{dataset['id']}/write",
        json=_json,
    )
    assert response.status_code == 200
    response = await client.get(
        f"/namespaces/{namespace['id']}/datasets/{dataset['id']}/read"
    )
    assert response.status_code == 200
    assert response.json() == _json
