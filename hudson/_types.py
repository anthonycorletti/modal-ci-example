import base64
import json
import sys
from datetime import datetime
from enum import Enum, unique
from typing import Dict, List, Optional

from docarray.document.pydantic_model import PydanticDocumentArray
from pydantic import BaseModel, Json, StrictInt, StrictStr, validator


@unique
class DeliveryType(str, Enum):
    # PULL = "pull" – TODO: coming soon!
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
    asgi: Optional[Dict]
    http_version: StrictStr
    method: StrictStr
    scheme: StrictStr
    root_path: Optional[StrictStr]
    path: StrictStr
    raw_path: Optional[str]
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


class Message(BaseModel):
    data: StrictStr

    @validator("data", pre=True, always=True)
    def validate_data_is_less_than_10mb(cls: BaseModel, v: str) -> str:
        if sys.getsizeof(v) > 10_000_000:
            raise ValueError("Message data must be less than or equal to 10MB.")
        try:
            json.loads(base64.b64decode(v.encode("utf-8")).decode("utf-8"))
        except json.JSONDecodeError:
            raise ValueError("Message data must be a valid base64 encoded JSON string.")
        return v

    class Config:
        schema_extra = {
            "example": {
                "data": {"message": "Hello world!"},
            }
        }
