import os
import sys
from typing import Dict

from pydantic import BaseSettings, Field


class _Env(BaseSettings):
    #
    #   Required
    #
    API_SECRET_KEY: str = Field(
        ...,
        env="API_SECRET_KEY",
        description="The API secret key.",
    )
    #
    #   Optional
    #
    LOG_LEVEL: str = Field(
        "INFO",
        env="LOG_LEVEL",
        description="Log level.",
    )
    PSQL_URL: str = Field(
        "postgresql+asyncpg://modalci:modalci@localhost:5432/modalci",
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
    VOLUMES: Dict[str, str] = Field(
        dict(),
        env="VOLUMES",
        description="Remote volumes specifications; formatted as "
        "{volume_name: volume_mount_location} where volume_mount_location is an "
        "absolute path.",
    )

    def to_modal_secret(self) -> Dict[str, str]:
        _result = self.dict()
        for k, v in _result.items():
            if isinstance(v, bool):
                _result[k] = str(v).lower()
            elif not isinstance(v, str):
                _result[k] = str(v)
        return _result

    class Config:
        env_file = ".env.local"
        env_encoding = "utf-8"


env = _Env()
if "pytest" in "".join(sys.argv):
    env = _Env(_env_file=".env.test")

# if the ENV_FILE environment variable is set, use it
# this is useful for running alembic migrations against remote databases
if os.getenv("ENV_FILE") is not None:
    env = _Env(_env_file=os.environ["ENV_FILE"])  # pragma: no cover
