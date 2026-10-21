import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import create_app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "vector-engine-alan-vo"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check_db(client: AsyncClient):
    response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"