from datetime import datetime

from docarray.document.pydantic_model import PydanticDocumentArray
from pydantic import BaseModel, StrictStr


class HealthResponse(BaseModel):
    message: StrictStr
    version: StrictStr
    time: datetime


class BaseResponse(BaseModel):
    pass


class DatasetCreateResponse(BaseResponse):
    pass


class DatasetGetResponse(BaseResponse):
    pass


class DatasetCreate(BaseModel):
    dataset: PydanticDocumentArray

    class Config:
        schema_extra = {
            "example": {
                "items": [
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
