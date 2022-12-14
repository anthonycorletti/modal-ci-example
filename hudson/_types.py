from datetime import datetime
from enum import Enum, unique
from typing import Dict, List

from docarray.document.pydantic_model import PydanticDocumentArray
from pydantic import BaseModel, Json, StrictInt, StrictStr


@unique
class DeliveryType(str, Enum):
    PULL = "pull"
    PUSH = "push"


class HealthResponse(BaseModel):
    message: StrictStr
    version: StrictStr
    time: datetime


class DataArray(BaseModel):
    data: PydanticDocumentArray

    class Config:
        schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "1",
                        "text": "hello",
                        "tags": {"foo": "bar"},
                        "embedding": [0.1, 0.2, 0.3],
                    },
                    {
                        "id": "2",
                        "text": "world",
                        "tags": {"foo": "bar"},
                        "embedding": [0.1, 0.2, 0.3],
                    },
                ]
            }
        }


class Scope(BaseModel):
    type: StrictStr
    asgi: Dict
    http_version: StrictStr
    method: StrictStr
    scheme: StrictStr
    root_path: StrictStr
    path: StrictStr
    raw_path: str
    headers: List
    query_string: bytes


class RequestLoggerMessage(BaseModel):
    scope: Scope
    _stream_consumed: bool
    _is_disconnected: bool


class ResponseLoggerMessage(BaseModel):
    status_code: StrictInt
    body: Json
    raw_headers: List
