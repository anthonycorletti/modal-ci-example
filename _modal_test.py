import os

import modal
import pytest

from settings import _Env

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
    return path.endswith((".coveragerc", "const.py", "settings.py"))


@stub.function(
    image=image,
    mounts=[
        # Dont need this as modal will mount the modalci package by default
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
            remote_dir="/root/static",
            local_dir=f"{os.environ['HOME']}/modal-ci-example/static",
        ),
        modal.Mount(
            remote_dir="/root/templates",
            local_dir=f"{os.environ['HOME']}/modal-ci-example/templates",
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
