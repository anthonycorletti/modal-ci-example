from datetime import datetime
from typing import Dict, List

from docarray.document.pydantic_model import PydanticDocumentArray
from pydantic import BaseModel, Json, StrictInt, StrictStr
from starlette.datastructures import Headers, MutableHeaders, QueryParams


class HealthResponse(BaseModel):
    message: StrictStr
    version: StrictStr
    time: datetime


class BaseResponse(BaseModel):
    pass


class CreateDatasetResponse(BaseResponse):
    pass


class GetDatasetResponse(BaseResponse):
    pass


class DeleteDatasetResponse(BaseResponse):
    pass


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


class RequestLoggerMessage(BaseModel):
    scope: Dict
    _stream_consumed: bool
    _is_disconnected: bool
    _query_params: QueryParams
    _headers: Headers
    _cookies: Dict


class ResponseLoggerMessage(BaseModel):
    status_code: StrictInt
    body: Json
    raw_headers: List
    _headers: MutableHeaders
