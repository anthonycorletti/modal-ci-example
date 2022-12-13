from typing import Generator

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from hudson.server.main import app as server_app


@pytest.fixture(scope="session")
def client() -> Generator:
    with TestClient(app=server_app) as client:
        yield client


@pytest.fixture(scope="function")
def runner() -> Generator:
    runner = CliRunner()
    yield runner
