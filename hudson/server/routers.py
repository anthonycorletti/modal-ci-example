from datetime import datetime

from fastapi import APIRouter, Body

from hudson import __version__
from hudson._types import (
    DatasetCreate,
    DatasetCreateResponse,
    DatasetGetResponse,
    HealthResponse,
)
from hudson.server.log import log

health_router = APIRouter(tags=["health"])
datasets_router = APIRouter(tags=["datasets"])
pubsub_router = APIRouter(tags=["pubsub"])


@health_router.get("/healthcheck", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    response = HealthResponse(message="⛵️", version=__version__, time=datetime.utcnow())
    log.debug(response.json)
    return response


@datasets_router.post("/datasets", response_model=DatasetCreateResponse)
async def create_datasets(dataset: DatasetCreate = Body(...)) -> DatasetCreateResponse:
    log.info(dataset.json())
    return DatasetCreateResponse(dataset=dataset.dataset)


@datasets_router.get("/datasets", response_model=DatasetGetResponse)
async def get_datasets() -> DatasetGetResponse:
    return DatasetGetResponse()


@pubsub_router.post("/topics")
async def create_topic():
    pass


@pubsub_router.post("/subscriptions")
async def create_subscription():
    pass


@pubsub_router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: str):
    pass


@pubsub_router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: str):
    # deletes all associated subscriptions before deleting the topic
    pass


@pubsub_router.post("/publish")
async def publish():
    pass
