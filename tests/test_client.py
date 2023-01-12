from unittest import mock
from uuid import UUID


from hudson import hudson_client
from hudson.exc import BaseHudsonException
from tests.mocks import MockNamespace, MockResponse


def test_base_exception() -> None:
    assert issubclass(BaseHudsonException, Exception)


@mock.patch(
    "hudson.client.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_create_namespace(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.create_namespace("default")
    assert ns.name == "default"


@mock.patch(
    "hudson.client.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_get_namespace(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.get_namespace(UUID(str(MockNamespace["id"])))
    assert ns.name == "default"


@mock.patch(
    "hudson.client.Client.request",
    return_value=MockResponse(status_code=200, json=MockNamespace),
)
async def test_delete_namespace(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.delete_namespace(UUID(str(MockNamespace["id"])))
    assert ns.name == "default"


@mock.patch(
    "hudson.client.Client.request",
    return_value=MockResponse(status_code=200, json=[MockNamespace]),
)
async def test_list_namespaces(mock_request: mock.MagicMock) -> None:
    ns = hudson_client.list_namespaces("default")
    assert ns[0].name == "default"
