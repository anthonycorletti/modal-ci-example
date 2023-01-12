from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import UUID4, AnyHttpUrl, BaseModel, validator
from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, ForeignKey, Relationship, SQLModel

from hudson._types import DeliveryType


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


class UUIDMixin(BaseModel):
    id: UUID4 = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class BaseNamespace(SQLModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        unique=True,
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "hudson",
            }
        }


class NamespaceCreate(BaseNamespace):
    ...


class Namespace(
    BaseNamespace,
    UUIDMixin,
    TimestampsMixin,
    table=True,
):
    __tablename__ = "namespaces"

    topics: List["Topic"] = Relationship(
        back_populates="namespace",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
        },
    )


class NamespaceRead(
    BaseNamespace,
    UUIDMixin,
    TimestampsMixin,
):
    topics: List["Topic"]


class BaseTopic(SQLModel):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "default",
            }
        }


class TopicCreate(BaseTopic):
    namespace_id: UUID4


class Topic(
    BaseTopic,
    UUIDMixin,
    TimestampsMixin,
    table=True,
):
    __tablename__ = "topics"

    __table_args__ = (
        UniqueConstraint(
            "namespace_id",
            "name",
        ),
    )

    namespace_id: UUID4 = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "namespaces.id",
                ondelete="CASCADE",
            ),
            index=True,
            nullable=False,
        ),
    )
    namespace: Namespace = Relationship(
        back_populates="topics",
        sa_relationship_kwargs={
            "lazy": "selectin",
        },
    )
    subscriptions: List["Subscription"] = Relationship(
        back_populates="topic",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
        },
    )


class TopicRead(
    BaseTopic,
    UUIDMixin,
    TimestampsMixin,
):
    namespace: Namespace
    subscriptions: List["Subscription"]


class BaseSubscription(SQLModel):
    name: str
    delivery_type: DeliveryType
    # TODO: needed for pull
    # message_retention_duration_minutes: int = Field(..., ge=0, le=7 * 24 * 60)
    push_endpoint: Optional[AnyHttpUrl]

    @validator("push_endpoint", pre=True, always=True)
    def validate_push_endpoint_https(
        cls,
        v: AnyHttpUrl,
    ) -> AnyHttpUrl:
        if v is not None and not v.startswith("https://"):
            raise ValueError("push_endpoint must be a HTTPS URL")
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "default",
                "delivery_type": "push",
            }
        }


class SubscriptionCreate(BaseSubscription):
    topic_id: UUID4


class Subscription(
    BaseSubscription,
    UUIDMixin,
    TimestampsMixin,
    table=True,
):
    __tablename__ = "subscriptions"

    __table_args__ = (
        UniqueConstraint(
            "topic_id",
            "name",
        ),
    )

    topic_id: UUID4 = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "topics.id",
                ondelete="CASCADE",
            ),
            index=True,
            nullable=False,
        ),
    )
    topic: Topic = Relationship(
        back_populates="subscriptions",
        sa_relationship_kwargs={
            "lazy": "selectin",
        },
    )


class SubscriptionRead(
    BaseSubscription,
    UUIDMixin,
    TimestampsMixin,
):
    topic: Topic


NamespaceRead.update_forward_refs()
TopicRead.update_forward_refs()
