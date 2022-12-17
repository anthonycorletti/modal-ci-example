from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

from hudson import __version__
from hudson._types import DataArray, HealthResponse, Message
from hudson.db import psql_db
from hudson.models import (
    Dataset,
    DatasetCreate,
    DatasetRead,
    Namespace,
    NamespaceCreate,
    NamespaceRead,
    Subscription,
    SubscriptionCreate,
    SubscriptionRead,
    Topic,
    TopicCreate,
    TopicRead,
)
from hudson.server.log import log
from hudson.server.services import (
    datasets_service,
    namespace_service,
    subscriptions_service,
    topics_service,
)
from hudson.server.utils import _APIRoute

health_router = APIRouter(route_class=_APIRoute, tags=["health"])
dataset_router = APIRouter(route_class=_APIRoute, tags=["dataset"])
namespace_router = APIRouter(route_class=_APIRoute, tags=["namespace"])
pubsub_router = APIRouter(route_class=_APIRoute, tags=["pubsub"])


@health_router.get("/healthcheck", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Get the health of the server.

    Returns:
        HealthResponse: The health of the server.
    """
    log.info("Healthcheck")
    return HealthResponse(message="⛵️", version=__version__, time=datetime.utcnow())


@namespace_router.post("/namespaces", response_model=NamespaceRead)
async def create_namespaces(
    namespace_create: NamespaceCreate = Body(...),
    psql: AsyncSession = Depends(psql_db),
) -> Namespace:
    """Create a namespace if it does not exist.

    Args:
        namespace_create (NamespaceCreate): The namespace to create.

    Returns:
        Namespace: The created namespace.
    """
    namespace = await namespace_service.get_by_name(
        name=namespace_create.name, psql=psql
    )
    if namespace is not None:
        return namespace
    return await namespace_service.create(namespace_create=namespace_create, psql=psql)


@namespace_router.get("/namespaces", response_model=List[NamespaceRead])
async def get_namespaces(
    name: Optional[str] = None, psql: AsyncSession = Depends(psql_db)
) -> List[Namespace]:
    """Get all namespaces.

    Args:
        name (Optional[str], optional): The namespace name. Defaults to None.

    Returns:
        List[Namespace]: The namespaces.
    """
    return await namespace_service.list(name=name, psql=psql)


@namespace_router.get("/namespaces/{namespace_id}", response_model=NamespaceRead)
async def get_namespace(
    namespace_id: UUID4, psql: AsyncSession = Depends(psql_db)
) -> Namespace:
    """Get a namespace.

    Args:
        namespace_id (UUID4): The namespace id.

    Returns:
        Namespace: The namespace.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    return namespace


@namespace_router.delete("/namespaces/{namespace_id}", response_model=NamespaceRead)
async def delete_namespaces(
    namespace_id: UUID4, psql: AsyncSession = Depends(psql_db)
) -> Namespace:
    """Delete a namespace.

    Args:
        namespace_id (UUID4): The namespace id.

    Returns:
        Namespace: The deleted namespace.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    return await namespace_service.delete(namespace_id=namespace_id, psql=psql)


@pubsub_router.get("/namespaces/{namespace_id}/topics", response_model=List[TopicRead])
async def get_topics(
    namespace_id: UUID4,
    name: Optional[str] = None,
    psql: AsyncSession = Depends(psql_db),
) -> List[Topic]:
    """Get all topics in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        name (Optional[str], optional): The topic name. Defaults to None.

    Returns:
        List[Topic]: The topics.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    return await topics_service.list(namespace_id=namespace_id, name=name, psql=psql)


@pubsub_router.post("/namespaces/{namespace_id}/topics", response_model=TopicRead)
async def create_topics(
    namespace_id: UUID4,
    topic_create: TopicCreate = Body(...),
    psql: AsyncSession = Depends(psql_db),
) -> Topic:
    """Create a topic in a namespace if it does not exist.

    Args:
        namespace_id (UUID4): The namespace id.
        topic_create (TopicCreate): The topic to create. Defaults to Body(...).

    Returns:
        Topic: The created topic.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    topic_create.namespace_id = namespace_id
    return await topics_service.create(topic_create=topic_create, psql=psql)


@pubsub_router.delete(
    "/namespaces/{namespace_id}/topics/{topic_id}", response_model=TopicRead
)
async def delete_topics(
    namespace_id: UUID4, topic_id: UUID4, psql: AsyncSession = Depends(psql_db)
) -> Topic:
    """Delete a topic in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        topic_id (UUID4): The topic id.

    Returns:
        Topic: The deleted topic.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    topic = await topics_service.get(
        topic_id=topic_id, namespace_id=namespace_id, psql=psql
    )
    if topic is None:
        raise HTTPException(status_code=400, detail="Topic not found.")
    return await topics_service.delete(
        topic_id=topic_id, namespace_id=namespace_id, psql=psql
    )


@pubsub_router.post(
    "/namespaces/{namespace_id}/topics/{topic_id}/subscriptions",
    response_model=SubscriptionRead,
)
async def create_subscriptions(
    namespace_id: UUID4,
    topic_id: UUID4,
    subscription_create: SubscriptionCreate = Body(...),
    psql: AsyncSession = Depends(psql_db),
) -> Subscription:
    """Create a subscription to a topic in a namespace if it does not exist.

    Args:
        namespace_id (UUID4): The namespace id.
        topic_id (UUID4): The topic id.
        subscription_create (SubscriptionCreate): The subscription to create.
            Defaults to Body(...).

    Returns:
        Subscription: The created subscription.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    topic = await topics_service.get(
        topic_id=topic_id, psql=psql, namespace_id=namespace_id
    )
    if topic is None:
        raise HTTPException(status_code=400, detail="Topic not found.")
    return await subscriptions_service.create(
        subscription_create=subscription_create, psql=psql
    )


@pubsub_router.get(
    "/namespaces/{namespace_id}/topics/{topic_id}/subscriptions",
    response_model=List[SubscriptionRead],
)
async def get_subscriptions(
    namespace_id: UUID4,
    topic_id: UUID4,
    name: Optional[str] = None,
    psql: AsyncSession = Depends(psql_db),
) -> List[Subscription]:
    """Get all subscriptions to a topic in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        topic_id (UUID4): The topic id.
        name (Optional[str], optional): The subscription name. Defaults to None.

    Returns:
        List[Subscription]: The subscriptions.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    topic = await topics_service.get(
        topic_id=topic_id, psql=psql, namespace_id=namespace_id
    )
    if topic is None:
        raise HTTPException(status_code=400, detail="Topic not found.")
    return await subscriptions_service.list(
        topic_id=topic_id, namespace_id=namespace_id, name=name, psql=psql
    )


@pubsub_router.delete(
    "/namespaces/{namespace_id}/topics/{topic_id}/subscriptions/{subscription_id}",
    response_model=SubscriptionRead,
)
async def delete_subscriptions(
    namespace_id: UUID4,
    topic_id: UUID4,
    subscription_id: UUID4,
    psql: AsyncSession = Depends(psql_db),
) -> Subscription:
    """Delete a subscription to a topic in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        topic_id (UUID4): The topic id.
        subscription_id (UUID4): The subscription id.

    Returns:
        Subscription: The deleted subscription.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    topic = await topics_service.get(
        topic_id=topic_id, psql=psql, namespace_id=namespace_id
    )
    if topic is None:
        raise HTTPException(status_code=400, detail="Topic not found.")
    subscription = await subscriptions_service.get(
        subscription_id=subscription_id,
        topic_id=topic_id,
        namespace_id=namespace_id,
        psql=psql,
    )
    if subscription is None:
        raise HTTPException(status_code=400, detail="Subscription not found.")
    return await subscriptions_service.delete(
        subscription_id=subscription_id,
        topic_id=topic_id,
        namespace_id=namespace_id,
        psql=psql,
    )


@pubsub_router.post(
    "/namespaces/{namespace_id}/topics/{topic_id}/publish",
    response_model=None,
)
async def publish_message_to_topic(
    namespace_id: UUID4,
    topic_id: UUID4,
    message: Message = Body(...),
    psql: AsyncSession = Depends(psql_db),
) -> None:
    """Publish a message to a topic in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        topic_id (UUID4): The topic id.
        message (Message): The message to publish.

    Returns:
        None.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    topic = await topics_service.get(
        topic_id=topic_id, namespace_id=namespace_id, psql=psql
    )
    if topic is None:
        raise HTTPException(status_code=400, detail="Topic not found.")
    return await topics_service.publish_message(topic=topic, message=message)


@dataset_router.post("/namespaces/{namespace_id}/datasets", response_model=DatasetRead)
async def create_datasets(
    namespace_id: UUID4,
    dataset_create: DatasetCreate = Body(...),
    psql: AsyncSession = Depends(psql_db),
) -> Dataset:
    """Create a dataset in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        dataset_create (DatasetCreate): The dataset to create.

    Returns:
        Dataset: The Dataset
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    result = await datasets_service.create(dataset_create=dataset_create, psql=psql)
    # TODO: hudson only supports writing to a dir on a filesystem now
    # hudson will support writing to s3, gcs, huggingface, etc in the future
    await datasets_service.create_directory_for_dataset(dataset=result)
    return result


@dataset_router.get(
    "/namespaces/{namespace_id}/datasets", response_model=List[DatasetRead]
)
async def get_datasets(
    namespace_id: UUID4,
    name: Optional[str] = None,
    psql: AsyncSession = Depends(psql_db),
) -> List[Dataset]:
    """Get all datasets in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        name (Optional[str], optional): The name of the dataset. Defaults to None.

    Returns:
        List[Dataset]: The datasets.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    return await datasets_service.list(name=name, psql=psql, namespace_id=namespace_id)


@dataset_router.get(
    "/namespaces/{namespace_id}/datasets/{dataset_id}", response_model=DatasetRead
)
async def get_dataset(
    namespace_id: UUID4, dataset_id: UUID4, psql: AsyncSession = Depends(psql_db)
) -> Dataset:
    """Get a dataset in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        dataset_id (UUID4): The dataset id.

    Returns:
        Dataset: The dataset.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    dataset = await datasets_service.get(
        dataset_id=dataset_id, namespace_id=namespace_id, psql=psql
    )
    if dataset is None:
        raise HTTPException(status_code=400, detail="Dataset not found.")
    return dataset


@dataset_router.delete(
    "/namespaces/{namespace_id}/datasets/{dataset_id}", response_model=DatasetRead
)
async def delete_datasets(
    namespace_id: UUID4, dataset_id: UUID4, psql: AsyncSession = Depends(psql_db)
) -> Dataset:
    """Delete a dataset in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        dataset_id (UUID4): The dataset id.

    Returns:
        Dataset.
    """
    namespace = await namespace_service.get(namespace_id=namespace_id, psql=psql)
    if namespace is None:
        raise HTTPException(status_code=400, detail="Namespace not found.")
    dataset = await datasets_service.get(
        dataset_id=dataset_id, namespace_id=namespace_id, psql=psql
    )
    if dataset is None:
        raise HTTPException(status_code=400, detail="Dataset not found.")
    return await datasets_service.delete(
        dataset_id=dataset_id, namespace_id=namespace_id, psql=psql
    )


@dataset_router.post(
    "/namespaces/{namespace_id}/datasets/{dataset_id}/write", response_model=None
)
async def write_to_datasets(
    namespace_id: UUID4, dataset_id: UUID4, data_array: DataArray = Body(...)
) -> None:
    """Write to a dataset in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        dataset_id (UUID4): The dataset id.
        data_array (DataArray): The data to write.

    Returns:
        None.
    """
    return await datasets_service.write(
        namespace_id=namespace_id, dataset_id=dataset_id, data_array=data_array
    )


@dataset_router.get(
    "/namespaces/{namespace_id}/datasets/{dataset_id}/read", response_model=DataArray
)
async def read_from_datasets(namespace_id: UUID4, dataset_id: UUID4) -> DataArray:
    """Read from a dataset in a namespace.

    Args:
        namespace_id (UUID4): The namespace id.
        dataset_id (UUID4): The dataset id.

    Returns:
        DataArray.
    """
    return await datasets_service.read(
        namespace_id=namespace_id,
        dataset_id=dataset_id,
    )
