import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Test root status endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to AI PlacementOS API"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    """Test /api/v1/health endpoint returns 200 and healthy DB connection."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert data["app_name"] == "AI PlacementOS"
    assert "llm_provider" in data


@pytest.mark.asyncio
async def test_ping_endpoint(async_client: AsyncClient):
    """Test /api/v1/ping endpoint."""
    response = await async_client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
