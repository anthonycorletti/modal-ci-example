from typing import Any, Optional
from uuid import uuid4

from hudson._types import DataArray


class MockResponse:
    def __init__(
        self,
        status_code: int,
        json: Any = None,
        is_success: bool = True,
        text: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self._json = json
        self.is_success = not str(status_code).startswith(("4", "5"))
        self.text = text

    def json(self) -> Any:
        return self._json


MockNamespace = {
    "id": uuid4(),
    "name": "default",
    "created_at": "2021-01-01T00:00:00+00:00",
    "updated_at": "2021-01-01T00:00:00+00:00",
    "topics": [],
    "datasets": [],
}


MockDataset = {
    "id": uuid4(),
    "name": "default",
    "namespace_id": uuid4(),
    "created_at": "2021-01-01T00:00:00+00:00",
    "updated_at": "2021-01-01T00:00:00+00:00",
    "namespace": MockNamespace,
}


MockDataArray = DataArray.Config.schema_extra["example"]
