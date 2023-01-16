from unittest import mock
from uuid import UUID

import pytest

from modalci import modalci_client
from modalci.exc import BasemodalciException
from tests.mocks import MockNamespace, MockResponse


def test_base_exception() -> None:
    assert issubclass(BasemodalciException, Exception)


@mock.patch(
    "modalci.client.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_create_namespace(mock_request: mock.MagicMock) -> None:
    ns = modalci_client.create_namespace("default")
    assert ns.name == "default"


@mock.patch(
    "modalci.client.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_get_namespace(mock_request: mock.MagicMock) -> None:
    ns = modalci_client.get_namespace(UUID(str(MockNamespace["id"])))
    assert ns.name == "default"


@mock.patch(
    "modalci.client.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_delete_namespace(mock_request: mock.MagicMock) -> None:
    ns = modalci_client.delete_namespace(UUID(str(MockNamespace["id"])))
    assert ns.name == "default"


@mock.patch(
    "modalci.client.Client.request",
    return_value=MockResponse(status_code=200, json=[MockNamespace]),
)
async def test_list_namespaces(mock_request: mock.MagicMock) -> None:
    ns = modalci_client.list_namespaces("default")
    assert ns[0].name == "default"


@mock.patch(
    "modalci.client.Client.request",
    return_value=MockResponse(status_code=500, text="Internal Server Error"),
)
async def test_client_returns_error(mock_request: mock.MagicMock) -> None:
    with pytest.raises(BasemodalciException):
        modalci_client.list_namespaces("default")
