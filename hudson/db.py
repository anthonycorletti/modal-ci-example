from typing import AsyncGenerator, Generator

import duckdb

# TODO: all sqlalchemy imports should be coming from sqlmodel
# once sqlmodel has full support for async
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from hudson._env import env


def _duck_db_connection(
    database_filename: str,
    read_only: bool = False,
) -> duckdb.DuckDBPyConnection:
    """Return a DuckDB database connection."""
    if not database_filename:
        database_filename = env.DUCK_DB
    return duckdb.connect(database=database_filename, read_only=read_only)


def duck_db(database_filename: str, read_only: bool = False) -> Generator:
    """Context manager for a DuckDB database connection."""
    db = _duck_db_connection(database_filename=database_filename, read_only=read_only)
    try:
        yield db
    finally:
        db.close()


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
