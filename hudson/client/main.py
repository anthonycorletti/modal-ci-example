from typing import Any, List, Optional, Union

from docarray import Document, DocumentArray
from httpx import Client
from httpx._types import HeaderTypes, QueryParamTypes, RequestContent, RequestData
from pydantic import UUID4

from hudson._env import env
from hudson._types import DataArray
from hudson.exc import BaseHudsonException
from hudson.models import DatasetRead, NamespaceRead


class HudsonClient(object):
    def __init__(self, url: str) -> None:
        self.url = url

    def request(
        self,
        method: str,
        path: str,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
    ) -> Any:
        with Client() as c:
            response = c.request(
                method=method,
                url=self.url + path,
                content=content,
                data=data,
                json=json,
                params=params,
                headers=headers,
                timeout=env.TIMEOUT_SECONDS,
            )
            if not response.is_success:
                raise BaseHudsonException(response.text)
            return response.json()

    def create_namespace(self, name: str) -> NamespaceRead:
        response = self.request(method="POST", path="/namespaces", json={"name": name})
        return NamespaceRead(**response)

    def get_namespace(self, namespace_id: UUID4) -> NamespaceRead:
        response = self.request(method="GET", path=f"/namespaces/{namespace_id}")
        return NamespaceRead(**response)

    def delete_namespace(self, namespace_id: UUID4) -> NamespaceRead:
        response = self.request(method="DELETE", path=f"/namespaces/{namespace_id}")
        return NamespaceRead(**response)

    def list_namespaces(self, name: str) -> List[NamespaceRead]:
        response = self.request(method="GET", path="/namespaces", params={"name": name})
        return [NamespaceRead(**item) for item in response]

    def create_dataset(
        self, namespace_id: UUID4, name: str, description: Optional[str] = None
    ) -> DatasetRead:
        _json = {"name": name, "namespace_id": str(namespace_id)}
        if description is not None:
            _json["description"] = description

        response = self.request(
            method="POST",
            path=f"/namespaces/{namespace_id}/datasets",
            json=_json,
        )

        return DatasetRead(**response)

    def get_dataset(self, namespace_id: UUID4, dataset_id: UUID4) -> DatasetRead:
        response = self.request(
            method="GET", path=f"/namespaces/{namespace_id}/datasets/{dataset_id}"
        )
        return DatasetRead(**response)

    def delete_dataset(self, namespace_id: UUID4, dataset_id: UUID4) -> DatasetRead:
        response = self.request(
            method="DELETE", path=f"/namespaces/{namespace_id}/datasets/{dataset_id}"
        )
        return DatasetRead(**response)

    def write_dataset(
        self,
        namespace_id: UUID4,
        dataset_id: UUID4,
        data: DocumentArray,
    ) -> None:
        _data = [d.to_pydantic_model().dict() for d in data]
        self.request(
            "POST",
            f"/namespaces/{namespace_id}/datasets/{dataset_id}/write",
            json={"data": _data},
        )
        return None

    def read_dataset(
        self,
        namespace_id: UUID4,
        dataset_id: UUID4,
        as_document_array: bool = True,
    ) -> Union[DocumentArray, DataArray]:
        response = self.request(
            method="GET",
            path=f"/namespaces/{namespace_id}/datasets/{dataset_id}/read",
        )
        da = DataArray(**response)
        if as_document_array:
            return DocumentArray([Document.from_pydantic_model(d) for d in da.data])
        return da


hudson_client = HudsonClient(url=env.HUDSON_SERVER_URL)
