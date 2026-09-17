import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient):
    """Test successful user registration returns access and refresh tokens."""
    payload = {
        "email": "student@placementos.ai",
        "password": "StrongPassword123!",
        "full_name": "Test Student",
        "role": "student",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "student@placementos.ai"
    assert data["user"]["role"] == "student"


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(async_client: AsyncClient):
    """Test duplicate registration with same email returns 422 error."""
    payload = {
        "email": "duplicate@placementos.ai",
        "password": "StrongPassword123!",
        "full_name": "First User",
    }
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 422
    err = res2.json()
    assert err["success"] is False
    assert err["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_register_short_password_fails(async_client: AsyncClient):
    """Test password shorter than 8 characters is rejected."""
    payload = {
        "email": "shortpass@placementos.ai",
        "password": "short",
        "full_name": "Short Pass User",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
