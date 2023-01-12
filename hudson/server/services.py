import asyncio
import base64
from typing import List, Optional

import httpx
from pydantic import UUID4
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from hudson._types import Message
from hudson.models import (
    Namespace,
    NamespaceCreate,
    Subscription,
    SubscriptionCreate,
    Topic,
    TopicCreate,
)


class NamespaceService:
    async def get_by_name(
        self,
        name: str,
        psql: AsyncSession,
    ) -> Optional[Namespace]:
        results = await psql.execute(select(Namespace).where(Namespace.name == name))
        return results.scalars().first()

    async def get(
        self,
        namespace_id: UUID4,
        psql: AsyncSession,
    ) -> Optional[Namespace]:
        results = await psql.execute(
            select(Namespace).where(Namespace.id == namespace_id)
        )
        return results.scalars().first()

    async def create(
        self,
        namespace_create: NamespaceCreate,
        psql: AsyncSession,
    ) -> Namespace:
        namespace = Namespace(name=namespace_create.name)
        psql.add(namespace)
        await psql.commit()
        await psql.refresh(namespace)
        return namespace

    async def list(
        self,
        name: Optional[str],
        psql: AsyncSession,
    ) -> List[Namespace]:
        if name is not None:
            results = (
                (
                    await psql.execute(
                        select(Namespace)
                        .where(Namespace.name.contains(name))  # type: ignore
                        .order_by(Namespace.name)
                    )
                )
                .scalars()
                .all()
            )
        else:
            results = (
                (await psql.execute(select(Namespace).order_by(Namespace.name)))
                .scalars()
                .all()
            )
        return results

    async def delete(
        self,
        namespace_id: UUID4,
        psql: AsyncSession,
    ) -> Namespace:
        results = await psql.execute(
            select(Namespace).where(Namespace.id == namespace_id)
        )
        namespace = results.scalars().first()
        if namespace:
            await psql.delete(namespace)
            await psql.commit()

        return namespace


class TopicsService:
    async def list(
        self,
        namespace_id: UUID4,
        name: Optional[str],
        psql: AsyncSession,
    ) -> List[Topic]:
        if name is not None:
            results = (
                (
                    await psql.execute(
                        select(Topic)
                        .where(
                            Topic.namespace_id == namespace_id,
                            Topic.name.contains(name),  # type: ignore
                        )
                        .order_by(Topic.name)
                    )
                )
                .scalars()
                .all()
            )
        else:
            results = (
                (
                    await psql.execute(
                        select(Topic)
                        .where(Topic.namespace_id == namespace_id)
                        .order_by(Topic.name)
                    )
                )
                .scalars()
                .all()
            )
        return results

    async def get(
        self,
        topic_id: UUID4,
        namespace_id: UUID4,
        psql: AsyncSession,
    ) -> Optional[Topic]:
        results = await psql.execute(
            select(Topic).where(
                Topic.id == topic_id,
                Topic.namespace_id == namespace_id,
            )
        )
        return results.scalars().first()

    async def create(
        self,
        topic_create: TopicCreate,
        psql: AsyncSession,
    ) -> Topic:
        results = await psql.execute(
            select(Topic).where(
                Topic.name == topic_create.name,
                Topic.namespace_id == topic_create.namespace_id,
            )
        )
        topic = results.scalars().first()
        if topic is not None:
            return topic
        topic = Topic(**topic_create.dict())
        psql.add(topic)
        await psql.commit()
        await psql.refresh(topic)
        return topic

    async def delete(
        self,
        topic_id: UUID4,
        namespace_id: UUID4,
        psql: AsyncSession,
    ) -> Topic:
        results = await psql.execute(
            select(Topic).where(
                Topic.id == topic_id,
                Topic.namespace_id == namespace_id,
            )
        )
        topic = results.scalars().first()
        if topic:
            await psql.delete(topic)
            await psql.commit()
        return topic

    async def publish_message(
        self,
        topic: Topic,
        message: Message,
    ) -> None:
        # TODO: hudson supports http-push publishing to HTTPS endpoints.
        # hudson should support other modes and other protocols in the future
        # e.g. pull, gRPC, websocket, carrier pigeon, idk, etc.
        await asyncio.gather(
            *[
                self.publish_message_to_subscription(
                    subscription=sub,
                    message=base64.b64decode(message.data.encode("utf-8")).decode(
                        "utf-8"
                    ),
                )
                for sub in topic.subscriptions
            ]
        )

    async def publish_message_to_subscription(
        self,
        subscription: Subscription,
        message: str,
    ) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                str(subscription.push_endpoint),
                json=message,
                headers={"Content-Type": "application/json"},
            )


class SubscriptionsService:
    async def create(
        self,
        subscription_create: SubscriptionCreate,
        psql: AsyncSession,
    ) -> Subscription:
        results = await psql.execute(
            select(Subscription).where(
                Subscription.name == subscription_create.name,
                Subscription.topic_id == subscription_create.topic_id,
            )
        )
        subscription = results.scalars().first()
        if subscription is not None:
            return subscription
        subscription = Subscription(**subscription_create.dict())
        psql.add(subscription)
        await psql.commit()
        await psql.refresh(subscription)
        return subscription

    async def list(
        self,
        namespace_id: UUID4,
        topic_id: UUID4,
        name: Optional[str],
        psql: AsyncSession,
    ) -> List[Subscription]:
        if name is not None:
            results = (
                (
                    await psql.execute(
                        select(Subscription)
                        .join(
                            Topic,
                            Subscription.topic_id == Topic.id,
                        )
                        .where(
                            Topic.namespace_id == namespace_id,
                            Subscription.topic_id == topic_id,
                            Subscription.name.contains(name),  # type: ignore
                        )
                        .order_by(Subscription.name)
                    )
                )
                .scalars()
                .all()
            )
        else:
            results = (
                (
                    await psql.execute(
                        select(Subscription)
                        .join(
                            Topic,
                            Subscription.topic_id == Topic.id,
                        )
                        .where(
                            Topic.namespace_id == namespace_id,
                            Subscription.topic_id == topic_id,
                        )
                        .order_by(Subscription.name)
                    )
                )
                .scalars()
                .all()
            )
        return results

    async def get(
        self,
        subscription_id: UUID4,
        topic_id: UUID4,
        namespace_id: UUID4,
        psql: AsyncSession,
    ) -> Optional[Subscription]:
        results = await psql.execute(
            select(Subscription)
            .join(Topic, Subscription.topic_id == Topic.id)
            .where(
                Subscription.id == subscription_id,
                Subscription.topic_id == topic_id,
                Topic.namespace_id == namespace_id,
            )
        )
        return results.scalars().first()

    async def delete(
        self,
        subscription_id: UUID4,
        topic_id: UUID4,
        namespace_id: UUID4,
        psql: AsyncSession,
    ) -> Subscription:
        results = await psql.execute(
            select(Subscription)
            .join(Topic, Subscription.topic_id == Topic.id)
            .where(
                Subscription.id == subscription_id,
                Subscription.topic_id == topic_id,
                Topic.namespace_id == namespace_id,
            )
        )
        subscription = results.scalars().first()
        if subscription:
            await psql.delete(subscription)
            await psql.commit()
        return subscription


namespace_service = NamespaceService()
topics_service = TopicsService()
subscriptions_service = SubscriptionsService()
