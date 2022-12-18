import asyncio
import base64
import json
import os
import shutil
import time
from pathlib import Path
from typing import List, Optional

import aiofiles
import httpx
import polars as pl
from pydantic import UUID4
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from hudson._env import env
from hudson._types import DataArray, Message
from hudson.models import (
    Dataset,
    DatasetCreate,
    Namespace,
    NamespaceCreate,
    Subscription,
    SubscriptionCreate,
    Topic,
    TopicCreate,
)


class NamespaceService:
    async def get_by_name(self, name: str, psql: AsyncSession) -> Optional[Namespace]:
        results = await psql.execute(select(Namespace).where(Namespace.name == name))
        return results.scalars().first()

    async def get(self, namespace_id: UUID4, psql: AsyncSession) -> Optional[Namespace]:
        results = await psql.execute(
            select(Namespace).where(Namespace.id == namespace_id)
        )
        return results.scalars().first()

    async def create(
        self, namespace_create: NamespaceCreate, psql: AsyncSession
    ) -> Namespace:
        namespace = Namespace(name=namespace_create.name)
        psql.add(namespace)
        await psql.commit()
        await psql.refresh(namespace)
        return namespace

    async def list(self, name: Optional[str], psql: AsyncSession) -> List[Namespace]:
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

    async def delete(self, namespace_id: UUID4, psql: AsyncSession) -> Namespace:
        results = await psql.execute(
            select(Namespace).where(Namespace.id == namespace_id)
        )
        namespace = results.scalars().first()
        if namespace:
            await psql.delete(namespace)
            await psql.commit()

        namespace_dir = Path(env.DATASETS_PATH) / str(namespace.id)
        if namespace_dir.exists():
            shutil.rmtree(namespace_dir)

        return namespace


class TopicsService:
    async def list(
        self, namespace_id: UUID4, name: Optional[str], psql: AsyncSession
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
        self, topic_id: UUID4, namespace_id: UUID4, psql: AsyncSession
    ) -> Optional[Topic]:
        results = await psql.execute(
            select(Topic).where(
                Topic.id == topic_id,
                Topic.namespace_id == namespace_id,
            )
        )
        return results.scalars().first()

    async def create(self, topic_create: TopicCreate, psql: AsyncSession) -> Topic:
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
        self, topic_id: UUID4, namespace_id: UUID4, psql: AsyncSession
    ) -> Topic:
        results = await psql.execute(
            select(Topic).where(
                Topic.id == topic_id, Topic.namespace_id == namespace_id
            )
        )
        topic = results.scalars().first()
        if topic:
            await psql.delete(topic)
            await psql.commit()
        return topic

    async def publish_message(self, topic: Topic, message: Message) -> None:
        # TODO: hudson supports http-push publishing to HTTPS endpoints.
        # hudson should support other modes and other protocols in the future
        # e.g. pull, gRPC, carrier pigeon, etc.
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
        self, subscription: Subscription, message: str
    ) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                str(subscription.push_endpoint),
                json=message,
                headers={"Content-Type": "application/json"},
            )


class SubscriptionsService:
    async def create(
        self, subscription_create: SubscriptionCreate, psql: AsyncSession
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
                        .join(Topic, Subscription.topic_id == Topic.id)
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
                        .join(Topic, Subscription.topic_id == Topic.id)
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


class DatasetsService:
    async def create(
        self, dataset_create: DatasetCreate, psql: AsyncSession
    ) -> Dataset:
        results = await psql.execute(
            select(Dataset).where(
                Dataset.name == dataset_create.name,
                Dataset.namespace_id == dataset_create.namespace_id,
            )
        )
        dataset = results.scalars().first()
        if dataset is not None:
            return dataset
        dataset = Dataset(**dataset_create.dict())
        psql.add(dataset)
        await psql.commit()
        await psql.refresh(dataset)
        return dataset

    async def create_directory_for_dataset(self, dataset: Dataset) -> None:
        dataset_path = (
            Path(env.DATASETS_PATH) / str(dataset.namespace_id) / str(dataset.id)
        )
        dataset_path.mkdir(parents=True, exist_ok=True)

    async def list(
        self,
        namespace_id: UUID4,
        name: Optional[str],
        psql: AsyncSession,
    ) -> List[Dataset]:
        if name is not None:
            results = (
                (
                    await psql.execute(
                        select(Dataset)
                        .where(
                            Dataset.namespace_id == namespace_id,
                            Dataset.name.contains(name),  # type: ignore
                        )
                        .order_by(Dataset.name)
                    )
                )
                .scalars()
                .all()
            )
        else:
            results = (
                (
                    await psql.execute(
                        select(Dataset)
                        .where(Dataset.namespace_id == namespace_id)
                        .order_by(Dataset.name)
                    )
                )
                .scalars()
                .all()
            )
        return results

    async def get(
        self, dataset_id: UUID4, namespace_id: UUID4, psql: AsyncSession
    ) -> Optional[Dataset]:
        results = await psql.execute(
            select(Dataset).where(
                Dataset.id == dataset_id,
                Dataset.namespace_id == namespace_id,
            )
        )
        return results.scalars().first()

    async def delete(
        self, dataset_id: UUID4, namespace_id: UUID4, psql: AsyncSession
    ) -> Dataset:
        results = await psql.execute(
            select(Dataset).where(
                Dataset.id == dataset_id, Dataset.namespace_id == namespace_id
            )
        )
        dataset = results.scalars().first()
        if dataset:
            await psql.delete(dataset)
            await psql.commit()

        dataset_path = Path(env.DATASETS_PATH) / str(namespace_id) / str(dataset_id)
        if dataset_path.exists():
            shutil.rmtree(dataset_path)

        return dataset

    async def write(
        self, namespace_id: UUID4, dataset_id: UUID4, data_array: DataArray
    ) -> None:
        dataset_path = (
            Path(env.DATASETS_PATH)
            / str(namespace_id)
            / str(dataset_id)
            / f"{int(time.time() * 1000)}.jsonl"
        )
        async with aiofiles.open(dataset_path, "w") as f:
            for d in data_array.data:
                await f.write(json.dumps(d.dict()))
        df = pl.read_ndjson(dataset_path)
        df.write_ipc(dataset_path.with_suffix(".arrow"))
        os.remove(dataset_path)

    async def read(
        self,
        namespace_id: UUID4,
        dataset_id: UUID4,
    ) -> DataArray:
        dataset_path = (
            Path(env.DATASETS_PATH) / str(namespace_id) / str(dataset_id) / "*.arrow"
        )
        df = pl.read_ipc(dataset_path)
        return DataArray(data=df.to_dicts())


namespace_service = NamespaceService()
topics_service = TopicsService()
subscriptions_service = SubscriptionsService()
datasets_service = DatasetsService()
