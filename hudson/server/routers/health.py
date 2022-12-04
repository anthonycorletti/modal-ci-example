from datetime import datetime

from fastapi import APIRouter

from hudson import __version__
from hudson.server.log import log
from hudson.types import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthcheck", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    response = HealthResponse(message="⛵️", version=__version__, time=datetime.utcnow())
    log.info(response.json)
    return response
