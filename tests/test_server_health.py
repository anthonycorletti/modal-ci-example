import os

from httpx import AsyncClient

from hudson import __version__


async def test_tz() -> None:
    assert os.environ["TZ"] == "UTC"


async def test_healthcheck(client: AsyncClient) -> None:
    response = await client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json()["message"] == "⛵️"
    assert response.json()["version"] == __version__
