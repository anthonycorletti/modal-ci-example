import os

from fastapi import FastAPI

from hudson import __version__
from hudson.const import HUDSON
from hudson.server import routers

os.environ["TZ"] = "UTC"

app = FastAPI(title=HUDSON, version=__version__)

app.include_router(routers.health_router)
app.include_router(routers.namespace_router)
app.include_router(routers.pubsub_router)
app.include_router(routers.dataset_router)
