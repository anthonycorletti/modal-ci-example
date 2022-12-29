import json
import os
import threading
from multiprocessing import active_children
from typing import Any, List, Optional, Union

from docarray import Document, DocumentArray
from httpx import Client
from httpx._types import HeaderTypes, QueryParamTypes, RequestContent, RequestData
from pydantic import UUID4
from watchfiles import Change, watch

from hudson._types import DataArray
from hudson.client.config import config
from hudson.exc import BaseHudsonException
from hudson.models import DatasetRead, NamespaceRead


class HudsonClient:
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
                timeout=config.timeout_seconds,
            )
            if not response.is_success:
                raise BaseHudsonException(response.text)
            return response.json()

    def create_namespace(self, name: str) -> NamespaceRead:
        response = self.request(method="POST", path="/namespaces", json={"name": name})
        config.namespace_id = UUID4(str(response["id"]))
        config.save_config()
        return NamespaceRead(**response)

    def set_namespace_id(self, namespace_id: UUID4) -> None:
        config.namespace_id = namespace_id
        config.save_config()

    def get_namespace(self, namespace_id: UUID4) -> NamespaceRead:
        response = self.request(method="GET", path=f"/namespaces/{namespace_id}")
        return NamespaceRead(**response)

    def delete_namespace(self, namespace_id: UUID4) -> NamespaceRead:
        response = self.request(method="DELETE", path=f"/namespaces/{namespace_id}")
        config.namespace_id = None
        config.dataset_id = None
        config.save_config()
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

        config.namespace_id = namespace_id
        config.dataset_id = UUID4(str(response["id"]))
        config.save_config()
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
        config.dataset_id = None
        config.save_config()
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

    def _watch(self, watch_dir: Optional[str] = None) -> None:
        if watch_dir is None:
            watch_dir = str(config.client_watch_dir)
        os.makedirs(watch_dir, exist_ok=True)

        for event in watch(watch_dir):
            for item in event:
                change, path = item[0], item[1]
                self._handle_watch_event(change, path)

    def _handle_watch_event(self, change: Change, path: str) -> None:
        if change == Change.added:
            self._handle_watch_added(path)
        elif change == Change.modified:
            self._handle_watch_modified(path)

    def _handle_watch_added(self, path: str) -> None:
        if path.endswith(".jsonl"):
            self._handle_watch_added_jsonl(path)
        elif path.endswith(".csv"):
            self._handle_watch_added_csv(path)
        else:
            raise ValueError(f"Unknown file type: {path}")

    def _upload_data_if_needed(self, path: str, data: DocumentArray) -> None:
        if len(data) >= config.min_batch_upload_size:
            assert (
                config.namespace_id is not None and config.dataset_id is not None
            ), "Namespace and dataset must be set before writing data. "
            self.write_dataset(
                namespace_id=config.namespace_id,
                dataset_id=config.dataset_id,
                data=data,
            )
            os.remove(path)
            return None

    def _handle_watch_added_jsonl(self, path: str) -> None:
        with open(path, "r") as f:
            data = [Document.from_json(json.loads(line)) for line in f.readlines()]
        self._upload_data_if_needed(path=path, data=DocumentArray(data))

    def _handle_watch_added_csv(self, path: str) -> None:
        with open(path, "r") as f:
            data = DocumentArray.from_csv(f)
        self._upload_data_if_needed(path=path, data=data)

    def _handle_watch_modified(self, path: str) -> None:
        if path.endswith(".jsonl"):
            self._handle_watch_modified_jsonl(path)
        elif path.endswith(".csv"):
            self._handle_watch_modified_csv(path)
        else:
            raise ValueError(f"Unknown file type: {path}")

    def _handle_watch_modified_jsonl(self, path: str) -> None:
        with open(path, "r") as f:
            data = [Document.from_json(json.loads(line)) for line in f.readlines()]
        self._upload_data_if_needed(path=path, data=DocumentArray(data))

    def _handle_watch_modified_csv(self, path: str) -> None:
        with open(path, "r") as f:
            data = DocumentArray.from_csv(f)
        self._upload_data_if_needed(path=path, data=data)

    def watch(self, watch_dir: Optional[str] = None) -> None:
        t = threading.Thread(
            name="hudson_watcher", target=self._watch, args=(watch_dir,)
        )
        t.start()

    def _stop_watch(self) -> None:
        processes = active_children()
        for process in processes:
            if process.name == "hudson_watcher":
                process.terminate()
        return None


hudson_client = HudsonClient(url=config.server_url)
