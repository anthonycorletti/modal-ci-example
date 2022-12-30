import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, List, Optional, Union

from docarray import Document, DocumentArray
from httpx import Client
from httpx._types import HeaderTypes, QueryParamTypes, RequestContent, RequestData
from pydantic import UUID4

from hudson._types import DataArray
from hudson.config import config
from hudson.exc import BaseHudsonException
from hudson.models import DatasetRead, NamespaceRead

pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="watcher-pool")
cleanup_pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="cleanup-pool")


class HudsonClient:
    def __init__(self, url: str) -> None:
        self.url = url
        self.client_watch_dir = config.client_watch_dir
        self.min_batch_upload_size = config.min_batch_upload_size
        self._run_watch = True

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

    def _case_and_upload(self, file_path: str) -> Optional[str]:
        with open(file_path, "r") as f:
            lines = f.readlines()
            if len(lines) >= self.min_batch_upload_size:
                # if so, upload the file
                assert (
                    config.namespace_id is not None and config.dataset_id is not None
                ), "Namespace and dataset must be set before writing data. "
                self.write_dataset(
                    namespace_id=config.namespace_id,
                    dataset_id=config.dataset_id,
                    data=[Document.from_json(line) for line in lines],
                )
                return file_path
            else:
                # else, do nothing
                return None

    def _watch(self, watch_dir: str) -> None:
        with pool as executor:
            while self._run_watch:
                future_to_path = {
                    executor.submit(
                        self._case_and_upload, f"{watch_dir}/{file}"
                    ): f"{watch_dir}/{file}"
                    for file in os.listdir(watch_dir)
                }
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        raise BaseHudsonException(
                            "Exception raised during stop._case_and_upload for "
                            f"{path}: {exc}"
                        )
                    else:
                        if result is not None:
                            os.remove(result)

    def watch(self, watch_dir: Optional[str] = None) -> None:
        if watch_dir is None:
            watch_dir = str(self.client_watch_dir)
        t = threading.Thread(target=self._watch, args=(watch_dir,), name="watcher-main")
        t.start()

    def stop(self) -> None:
        self._run_watch = False
        for thread in threading.enumerate():
            if thread.name == "watcher-main":
                thread.join()
        # for any file leftover in the watch_dir, upload it
        with cleanup_pool as executor:
            future_to_path = {
                executor.submit(
                    self._case_and_upload, f"{self.client_watch_dir}/{file}"
                ): f"{self.client_watch_dir}/{file}"
                for file in os.listdir(self.client_watch_dir)
            }
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                except Exception as exc:
                    raise BaseHudsonException(
                        "Exception raised during stop._case_and_upload for "
                        f"{path}: {exc}"
                    )
                else:
                    if result is not None:
                        os.remove(result)


hudson_client = HudsonClient(url=config.server_url)
