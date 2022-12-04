import os

from fastapi.testclient import TestClient

from hudson import __version__


def test_tz() -> None:
    assert os.environ["TZ"] == "UTC"


def test_healthcheck(client: TestClient) -> None:
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json()["message"] == "⛵️"
    assert response.json()["version"] == __version__
