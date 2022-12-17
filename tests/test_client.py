from unittest import mock
from uuid import UUID

import pytest
from docarray import Document, DocumentArray

from hudson import hudson_client
from hudson.exc import BaseHudsonException
from tests.mocks import MockDataset, MockNamespace, MockResponse


def test_base_exception() -> None:
    assert issubclass(BaseHudsonException, Exception)


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_create_namespace(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.create_namespace("default")
    assert ns.name == "default"


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_get_namespace(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.get_namespace(UUID(str(MockNamespace["id"])))
    assert ns.name == "default"


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_delete_namespace(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.delete_namespace(UUID(str(MockNamespace["id"])))
    assert ns.name == "default"


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200, json=[MockNamespace]),
)
async def test_list_namespaces(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.list_namespaces("default")
    assert ns[0].name == "default"


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200, json=MockDataset),
)
async def test_create_dataset(mock_request: mock.MagicMock) -> None:
    ds = hudson_client.create_dataset(UUID(str(MockNamespace["id"])), "default")
    assert ds.name == "default"


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200, json=MockDataset),
)
async def test_get_dataset(mock_request: mock.MagicMock) -> None:
    ds = hudson_client.get_dataset(
        namespace_id=UUID(str(MockNamespace["id"])),
        dataset_id=UUID(str(MockDataset["id"])),
    )
    assert ds.name == "default"


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200, json=MockDataset),
)
async def test_delete_dataset(mock_request: mock.MagicMock) -> None:
    ds = hudson_client.delete_dataset(
        namespace_id=UUID(str(MockNamespace["id"])),
        dataset_id=UUID(str(MockDataset["id"])),
    )
    assert ds.name == "default"


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=200),
)
async def test_write_dataset(mock_request: mock.MagicMock) -> None:
    hudson_client.write_dataset(
        namespace_id=UUID(str(MockNamespace["id"])),
        dataset_id=UUID(str(MockDataset["id"])),
        data=DocumentArray([Document(text="hello world")]),
    )


@mock.patch(
    "hudson.client.main.Client.request",
    return_value=MockResponse(status_code=500, text="Internal Server Error"),
)
async def test_client_returns_error(mock_request: mock.MagicMock) -> None:
    with pytest.raises(BaseHudsonException):
        hudson_client.write_dataset(
            namespace_id=UUID(str(MockNamespace["id"])),
            dataset_id=UUID(str(MockDataset["id"])),
            data=DocumentArray([Document(text="hello world")]),
        )
