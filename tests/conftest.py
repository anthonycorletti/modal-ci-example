import asyncio
import shutil
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typer.testing import CliRunner

from hudson._env import env
from hudson.db import async_psql_engine
from hudson.server.main import app as server_app


@pytest.fixture(scope="function")
def runner() -> Generator:
    runner = CliRunner()
    yield runner


@pytest.fixture(scope="session")
def event_loop(request: Request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator:
    async with AsyncClient(
        app=server_app,
        base_url=env.HUDSON_SERVER_URL,
    ) as client:
        yield client


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
    shutil.rmtree(env.DATASETS_PATH, ignore_errors=True)
