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

    class Config:
        env_file = ".env", ".env.local"
        env_encoding = "utf-8"


env = _Env()
