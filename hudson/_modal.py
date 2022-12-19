from typing import List

import modal

# TODO: use tomllib when 3.11 can be used with hudson, blocked by torch + others
import toml
from fastapi import FastAPI

from hudson._env import _Env
from hudson.server.main import app

stub = modal.Stub()

stub["env"] = modal.Secret(_Env(_env_file=".env").dict())


def _get_dependencies() -> List[str]:
    data = toml.load("pyproject.toml")
    return data["project"]["dependencies"]


image = modal.Image.debian_slim().pip_install(_get_dependencies())


@stub.asgi(
    image=image,
    secret=stub["env"],
    shared_volumes={
        stub["env"]["DATASETS_PATH"]: modal.SharedVolume().persist(
            stub["env"]["MODAL_VOLUME_NAME"]
        )
    },
)
def _app() -> FastAPI:
    return app


if __name__ == "__main__":
    stub.serve()
