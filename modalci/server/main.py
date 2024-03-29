import os
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from const import modalci
from modalci import __version__
from modalci.server import routers

os.environ["TZ"] = "UTC"

app = FastAPI(title=modalci, version=__version__)
app.mount(
    path="/static",
    app=StaticFiles(directory="static"),
    name="static",
)

app.include_router(routers.health_router)
app.include_router(routers.namespace_router)
app.include_router(routers.pubsub_router)
app.include_router(routers.home_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Seconds"] = str(process_time)
    return response
