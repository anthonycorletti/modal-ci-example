from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class TimestampsMixin(BaseModel):
    created_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False,
        )
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        )
    )


class BaseNamespace(SQLModel):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "hudson",
            }
        }


class CreateNamespace(BaseNamespace):
    pass


class Namespace(BaseNamespace, TimestampsMixin, table=True):
    __tablename__ = "namespaces"

    id: Optional[UUID4] = Field(default_factory=uuid4, primary_key=True, nullable=False)
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "hudson",
            }
        }


class ReadNamespace(BaseNamespace):
    id: UUID4
    created_at: datetime
    updated_at: datetime
