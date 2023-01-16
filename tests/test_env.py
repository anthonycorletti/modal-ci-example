from modalci.settings import _Env


def test_env_conversion() -> None:
    test_env = _Env(
        API_SECRET_KEY="test",
        PSQL_URL="postgresql+asyncpg://modalci:modalci@localhost:5432/modalci",
        PSQL_POOL_SIZE=5,
        PSQL_MAX_OVERFLOW=10,
        PSQL_POOL_PRE_PING=True,
    )
    s = test_env.to_modal_secret()
    assert s["API_SECRET_KEY"] == "test"
    assert (
        s["PSQL_URL"] == "postgresql+asyncpg://modalci:modalci@localhost:5432/modalci"
    )
    assert s["PSQL_POOL_SIZE"] == "5"
    assert s["PSQL_MAX_OVERFLOW"] == "10"
    assert s["PSQL_POOL_PRE_PING"] == "true"
