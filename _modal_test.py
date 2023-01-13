import os

import modal
import pytest

from hudson.const import STATIC_PATH, TEMPLATES_PATH
from hudson.settings import _Env

stub = modal.Stub("ci")
_s = _Env(_env_file=".env.test")
secrets = [
    modal.Secret(_s.to_modal_secret()),
    modal.Secret.from_name("hudson-test-psql-url"),
]
image = modal.Image.debian_slim().pip_install_from_pyproject(
    "pyproject.toml", optional_dependencies=["test", "dev"]
)


@stub.function(
    image=image,
    mounts=[
        modal.Mount(
            local_dir=f"{os.environ['HOME']}/hudson/hudson",
            remote_dir="/root/app/hudson",
        ),
        modal.Mount(
            local_dir=f"{os.environ['HOME']}/hudson/tests",
            remote_dir="/root/app/tests",
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
            "/root/app/tests",
            "--cov=hudson",
            "--cov=tests",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "-o",
            " console_output_style=progress",
            "--disable-warnings",
            "--cov-fail-under=100",
        ]
    )


if __name__ == "__main__":
    with stub.run():
        rcode = _pytest_modal()
        if rcode != 0:
            raise RuntimeError(f"pytest returned {rcode}")
