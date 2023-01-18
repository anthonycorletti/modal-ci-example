import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typer.testing import CliRunner

from modalci.config import config
from modalci.db import async_psql_engine
from modalci.server.main import app as server_app


@pytest.fixture(scope="function")
def runner() -> Generator:
    runner = CliRunner()
    yield runner


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator:
    async with AsyncClient(
        app=server_app,
        base_url="http://testserver:8001",
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def event_loop(request: Request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def async_db_session() -> AsyncGenerator:
    session = sessionmaker(
        async_psql_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session() as s:
        async with async_psql_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        yield s

    async with async_psql_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_psql_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def delete_test_database() -> AsyncGenerator:
    yield


async def _reset_client_config() -> None:
    if os.path.exists(config.config_path):
        os.remove(config.config_path)


@pytest.fixture(scope="function", autouse=True)
async def reset_client_config() -> AsyncGenerator:
    await _reset_client_config()
    yield
    await _reset_client_config()
