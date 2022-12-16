import os
import sys

from pydantic import BaseSettings, Field


class _Env(BaseSettings):
    LOG_LEVEL: str = Field(
        "INFO",
        env="LOG_LEVEL",
        description="Log level.",
    )
    API_SECRET_KEY: str = Field(
        ...,
        env="API_SECRET_KEY",
        description="The API secret key.",
    )
    DUCK_DB: str = Field(
        "hudson.db",
        env="DUCK_DB",
        description="The DuckDB database file.",
    )
    PSQL_URL: str = Field(
        "postgresql+asyncpg://hudson:hudson@localhost:5432/hudson",
        env="PSQL_URL",
        description="The PSQL database URL.",
    )
    PSQL_POOL_SIZE: int = Field(
        5,
        env="PSQL_POOL_SIZE",
        description="The PSQL database pool size.",
    )
    PSQL_MAX_OVERFLOW: int = Field(
        10,
        env="PSQL_MAX_OVERFLOW",
        description="The PSQL database max overflow.",
    )
    PSQL_POOL_PRE_PING: bool = Field(
        True,
        env="PSQL_POOL_PRE_PING",
        description="The PSQL database pre pool ping.",
    )
    DATASETS_PATH: str = Field(
        f"{os.environ['HOME']}/.hudson/datasets",
        env="DATASETS_PATH",
        description="The root dir for storing datasets.",
    )

    class Config:
        env_file = ".env", ".env.local"
        env_encoding = "utf-8"


env = _Env()
if "pytest" in "".join(sys.argv):
    env = _Env(_env_file=".env.test")
