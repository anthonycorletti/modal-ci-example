from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from hudson._env import env

async_psql_engine = create_async_engine(
    url=env.PSQL_URL,
    pool_size=env.PSQL_POOL_SIZE,
    max_overflow=env.PSQL_MAX_OVERFLOW,
    pool_pre_ping=env.PSQL_POOL_PRE_PING,
    future=True,
)


async def psql_db() -> AsyncGenerator:
    async_session = sessionmaker(
        async_psql_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
