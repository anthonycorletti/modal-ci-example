from typing import Any, List, Optional

from httpx import Client
from httpx._types import HeaderTypes, QueryParamTypes, RequestContent, RequestData
from pydantic import UUID4

from modalci.config import config
from modalci.exc import BasemodalciException
from modalci.models import NamespaceRead


class modalciClient:
    def __init__(self, url: str) -> None:
        self.url = url
        self._run_watch = True
        self.config = config

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
                timeout=config.timeout_seconds,
            )
            if not response.is_success:
                raise BasemodalciException(response.text)
            return response.json()

    def create_namespace(self, name: str) -> NamespaceRead:
        response = self.request(
            method="POST",
            path="/namespaces",
            json={"name": name},
        )
        config.namespace_id = UUID4(str(response["id"]))
        config.save()
        return NamespaceRead(**response)

    def get_namespace(self, namespace_id: UUID4) -> NamespaceRead:
        response = self.request(
            method="GET",
            path=f"/namespaces/{namespace_id}",
        )
        return NamespaceRead(**response)

    def delete_namespace(self, namespace_id: UUID4) -> NamespaceRead:
        response = self.request(
            method="DELETE",
            path=f"/namespaces/{namespace_id}",
        )
        config.namespace_id = None
        config.save()
        return NamespaceRead(**response)

    def list_namespaces(self, name: str) -> List[NamespaceRead]:
        response = self.request(
            method="GET",
            path="/namespaces",
            params={"name": name},
        )
        return [NamespaceRead(**item) for item in response]


modalci_client = modalciClient(url=config.server_url)
