from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine.base import Connection
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine
from typer.testing import CliRunner

from alembic import context
from hudson._env import env
from hudson.models import Namespace  # noqa
from hudson.server.main import app as server_app


@pytest.fixture(scope="session")
def client() -> Generator:
    with TestClient(app=server_app) as client:
        yield client


@pytest.fixture(scope="function")
def runner() -> Generator:
    runner = CliRunner()
    yield runner


# @pytest.fixture(scope="module", autouse=True)
# def event_loop() -> Generator:
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=SQLModel.metadata)

    with context.begin_transaction():
        context.run_migrations()


@pytest.fixture(scope="module", autouse=True)
async def reset_test_database() -> None:
    connectable = AsyncEngine(create_engine(env.PSQL_URL, future=True))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
