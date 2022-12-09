from datetime import datetime

from fastapi import APIRouter, Body

from hudson import __version__
from hudson._types import CreateDataResponse, DataArray, GetDataResponse, HealthResponse
from hudson.server.log import log
from hudson.server.utils import _APIRoute

health_router = APIRouter(route_class=_APIRoute, tags=["health"])
data_router = APIRouter(route_class=_APIRoute, tags=["data"])
pubsub_router = APIRouter(route_class=_APIRoute, tags=["ps"])


@health_router.get("/healthcheck", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Get the health of the server.

    Returns:
        HealthResponse: The health of the server.
    """
    return HealthResponse(message="⛵️", version=__version__, time=datetime.utcnow())


@data_router.post("/data", response_model=CreateDataResponse)
async def create_data(data: DataArray = Body(...)) -> CreateDataResponse:
    log.info(dir(data.data[0]))
    log.info(f"data.data[0].blob: {data.data[0].blob}")
    return CreateDataResponse(dataset=data.data)


@data_router.get("/data", response_model=GetDataResponse)
async def get_datasets() -> GetDataResponse:
    return GetDataResponse()


@pubsub_router.get("/topics")
async def get_topics() -> None:
    # TODO: get topics
    pass


@pubsub_router.post("/topics")
async def create_topics() -> None:
    # TODO: create topic
    pass


@pubsub_router.post("/topics")
async def delete_topics() -> None:
    # TODO: delete topics and associated subscriptions
    pass


@pubsub_router.get("/subscriptions")
async def get_subscriptions() -> None:
    # TODO: get subscriptions
    pass


@pubsub_router.post("/subscriptions")
async def create_subscriptions() -> None:
    # TODO: create subscriptions
    pass


@pubsub_router.post("/subscriptions")
async def delete_subscriptions() -> None:
    # TODO: delete subscriptions
    pass


@pubsub_router.post("/topics/{topic}/publish")
async def publish() -> None:
    # TODO: publish a message to a topic
    pass
