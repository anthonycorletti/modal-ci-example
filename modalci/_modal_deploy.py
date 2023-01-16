import modal
from fastapi import FastAPI

from modalci.const import STATIC_PATH, TEMPLATES_PATH
from modalci.server.main import app
from modalci.settings import _Env

stub = modal.Stub()

_s = _Env(_env_file=".env")
stub["env"] = modal.Secret(_s.to_modal_secret())
image = modal.Image.debian_slim().pip_install_from_pyproject("pyproject.toml")


@stub.asgi(
    image=image,
    secret=stub["env"],
    mounts=[
        modal.Mount("/root/static", local_dir=STATIC_PATH),
        modal.Mount("/root/templates", local_dir=TEMPLATES_PATH),
    ],
    shared_volumes={k: modal.SharedVolume().persist(v) for k, v in _s.VOLUMES.items()},
)
def _app() -> FastAPI:
    return app


if __name__ == "__main__":
    stub.serve()
