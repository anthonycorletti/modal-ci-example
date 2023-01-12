from pathlib import Path

import modal
from fastapi import FastAPI

from hudson.server.main import app
from hudson.settings import _Env

stub = modal.Stub()

_s = _Env(_env_file=".env")
stub["env"] = modal.Secret(_s.to_modal_secret())
image = modal.Image.debian_slim().pip_install_from_pyproject("pyproject.toml")

parent = Path(__file__).parent.parent
static_path = parent / "static"
templates_path = parent / "templates"


@stub.asgi(
    image=image,
    secret=stub["env"],
    mounts=[
        modal.Mount("/root/static", local_dir=static_path),
        modal.Mount("/root/templates", local_dir=templates_path),
    ],
    shared_volumes={k: modal.SharedVolume().persist(v) for k, v in _s.VOLUMES.items()},
)
def _app() -> FastAPI:
    return app


if __name__ == "__main__":
    stub.serve()
