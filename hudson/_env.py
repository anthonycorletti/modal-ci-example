import os
import sys
from typing import Dict

from pydantic import BaseSettings, Field


class _Env(BaseSettings):
    LOG_LEVEL: str = Field(
        "INFO",
        env="LOG_LEVEL",
        description="Log level.",
    )
    HUDSON_SERVER_URL: str = Field(
        "http://localhost:8000",
        env="HUDSON_SERVER_URL",
        description="The Hudson server URL.",
    )
    API_SECRET_KEY: str = Field(
        ...,
        env="API_SECRET_KEY",
        description="The API secret key.",
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
    TIMEOUT_SECONDS: int = Field(
        60,
        env="TIMEOUT_SECONDS",
        description="The timeout for HTTP requests.",
    )
    MODAL_VOLUME_NAME: str = Field(
        "hudson-datasets",
        env="MODAL_VOLUME_NAME",
        description="The Modal volume name for datasets.",
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
        env_file = ".env", ".env.local"
        env_encoding = "utf-8"


env = _Env()
if "pytest" in "".join(sys.argv):
    env = _Env(_env_file=".env.test")
