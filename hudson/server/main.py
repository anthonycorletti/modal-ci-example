import os

from fastapi import FastAPI

from hudson import __version__
from hudson.server.routers import health

os.environ["TZ"] = "UTC"

app = FastAPI(title="Hudson", version=__version__)

app.include_router(health.router)
