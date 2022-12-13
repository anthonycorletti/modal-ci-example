from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends
from pydantic import UUID4
from sqlmodel import column, select
from sqlmodel.ext.asyncio.session import AsyncSession

from hudson import __version__
from hudson._types import (
    CreateDatasetResponse,
    DataArray,
    DeleteDatasetResponse,
    GetDatasetResponse,
    HealthResponse,
)
from hudson.db import psql_db
from hudson.models import CreateNamespace, Namespace, ReadNamespace
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
    return HealthResponse(message="⛵️", version=__version__, time=datetime.utcnow())


@namespace_router.post("/namespaces", response_model=ReadNamespace)
async def create_namespaces(
    create_namespace: CreateNamespace = Body(...),
    psql: AsyncSession = Depends(psql_db),
) -> Namespace:
    """Create a namespace if it does not exist.

    Args:
        create_namespace (CreateNamespace): The namespace to create.
        psql (Session): The database session.

    Returns:
        Namespace: The created namespace.
    """
    results = await psql.execute(
        select(Namespace).where(Namespace.name == create_namespace.name)
    )
    namespace = results.scalars().first()
    if namespace is not None:
        return namespace
    namespace = Namespace(name=create_namespace.name)
    psql.add(namespace)
    await psql.commit()
    await psql.refresh(namespace)
    return namespace


@namespace_router.get("/namespaces", response_model=List[ReadNamespace])
async def get_namespaces(
    q: Optional[str] = None, psql: AsyncSession = Depends(psql_db)
) -> List[Namespace]:
    """Get all namespaces.

    Returns:
        List[Namespace]: The namespaces.
    """
    if q is not None:
        results = (
            (
                await psql.execute(
                    select(Namespace)
                    .where(column("name").contains(q))
                    .order_by(column("name"))
                )
            )
            .scalars()
            .all()
        )
    else:
        results = (
            (await psql.execute(select(Namespace).order_by(column("name"))))
            .scalars()
            .all()
        )
    return results


@namespace_router.delete("/namespaces/{namespace_id}", response_model=ReadNamespace)
async def delete_namespaces(
    namespace_id: UUID4, psql: AsyncSession = Depends(psql_db)
) -> Namespace:
    """Delete a namespace.

    Args:
        namespace_id (UUID4): The namespace id.

    Returns:
        Namespace: The deleted namespace.
    """
    results = await psql.execute(select(Namespace).where(Namespace.id == namespace_id))
    namespace = results.scalars().first()

    if namespace:
        await psql.delete(namespace)
        await psql.commit()
    return namespace


@pubsub_router.get("/namespace/{namespace_id}/topics")
async def get_topics(namespace_id: UUID4) -> None:
    # TODO: get topics
    pass


@pubsub_router.post("/namespace/{namespace_id}/topics")
async def create_topics(namespace_id: UUID4) -> None:
    # TODO: create topic
    pass


@pubsub_router.post("/namespace/{namespace_id}/topics")
async def delete_topics(namespace_id: UUID4) -> None:
    # TODO: delete topics and associated subscriptions
    pass


@pubsub_router.get("/namespace/{namespace_id}/subscriptions")
async def get_subscriptions(namespace_id: UUID4) -> None:
    # TODO: get subscriptions
    pass


@pubsub_router.post("/namespace/{namespace_id}/subscriptions")
async def create_subscriptions(namespace_id: UUID4) -> None:
    # TODO: create subscriptions
    pass


@pubsub_router.post("/namespace/{namespace_id}/subscriptions")
async def delete_subscriptions(namespace_id: UUID4) -> None:
    # TODO: delete subscriptions
    pass


@pubsub_router.post("/namespace/{namespace_id}/topics/{topic}/publish")
async def publish(namespace_id: UUID4) -> None:
    # TODO: publish a message to a topic
    pass


@dataset_router.post(
    "/namespace/{namespace_id}/datasets", response_model=CreateDatasetResponse
)
async def create_datasets(
    namespace_id: UUID4, data_array: DataArray = Body(...)
) -> None:
    # TODO: create datasets
    pass


@dataset_router.get(
    "/namespace/{namespace_id}/datasets", response_model=GetDatasetResponse
)
async def get_datasets(
    namespace_id: UUID4,
) -> None:
    # TODO: get datasets
    pass


@dataset_router.delete(
    "/namespace/{namespace_id}/datasets/{dataset_id}",
    response_model=DeleteDatasetResponse,
)
async def delete_datasets(namespace_id: UUID4, dataset_id: UUID4) -> None:
    # TODO: delete datasets
    pass
