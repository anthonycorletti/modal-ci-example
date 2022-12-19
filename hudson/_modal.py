from typing import List

import modal
import tomllib
from fastapi import FastAPI

from hudson._env import _Env
from hudson.server.main import app

stub = modal.Stub()

stub["env"] = modal.Secret(_Env(_env_file=".env").dict())


def _get_dependencies() -> List[str]:
    data = tomllib.load(open("pyproject.toml", "rb"))
    return data["project"]["dependencies"]


image = modal.Image.debian_slim().pip_install(_get_dependencies())


@stub.asgi(
    image=image,
    secret=stub["env"],
    shared_volumes={stub["env"]["DATASETS_PATH"]: modal.SharedVolume()},
)
def _app() -> FastAPI:
    return app


if __name__ == "__main__":
    stub.serve()
