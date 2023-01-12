import os
import time
from typing import Callable

from fastapi import FastAPI, Request, Response

from hudson import __version__
from hudson.const import HUDSON
from hudson.server import routers

os.environ["TZ"] = "UTC"

app = FastAPI(title=HUDSON, version=__version__)

app.include_router(routers.health_router)
app.include_router(routers.namespace_router)
app.include_router(routers.pubsub_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Seconds"] = str(process_time)
    return response
