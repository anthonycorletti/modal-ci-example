from bs4 import BeautifulSoup
from httpx import AsyncClient


async def test_home_page(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    assert soup.find("h1").text.strip() == "⛵️"
