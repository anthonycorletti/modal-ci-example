import os

import modal
import pytest

from modalci.const import STATIC_PATH, TEMPLATES_PATH
from modalci.settings import _Env

stub = modal.Stub("ci")

_s = _Env(_env_file=".env.test")
secrets = [
    modal.Secret(_s.to_modal_secret()),
    modal.Secret.from_name("modalci-test-psql-url"),
]
image = modal.Image.debian_slim().pip_install_from_pyproject(
    "pyproject.toml", optional_dependencies=["test", "dev"]
)


def _modalinclude(path: str) -> bool:
    return path.endswith(".coveragerc")


@stub.function(
    image=image,
    mounts=[
        modal.Mount(
            local_dir=f"{os.environ['HOME']}/modal-ci-example/modalci",
            remote_dir="/root/modalci",
        ),
        modal.Mount(
            local_dir=f"{os.environ['HOME']}/modal-ci-example/tests",
            remote_dir="/root/tests",
        ),
        modal.Mount(
            local_dir=f"{os.environ['HOME']}/modal-ci-example/",
            remote_dir="/root",
            condition=_modalinclude,
        ),
        modal.Mount(
            "/root/static",
            local_dir=STATIC_PATH,
        ),
        modal.Mount(
            "/root/templates",
            local_dir=TEMPLATES_PATH,
        ),
    ],
    secrets=secrets,
)
def _pytest_modal() -> int:
    return pytest.main(
        [
            "--cov=modalci",
            "--cov=tests",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--disable-warnings",
            "--cov-fail-under=100",
            "--asyncio-mode=auto",
        ]
    )


if __name__ == "__main__":
    with stub.run():
        rcode = _pytest_modal()
        if rcode != 0:
            raise RuntimeError(f"pytest returned {rcode}")
