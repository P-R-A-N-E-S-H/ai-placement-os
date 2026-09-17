import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_user_success(async_client: AsyncClient):
    """Test login with valid credentials returns tokens and user info."""
    reg_payload = {
        "email": "loginuser@placementos.ai",
        "password": "CorrectPassword123!",
        "full_name": "Login User",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "loginuser@placementos.ai",
        "password": "CorrectPassword123!",
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "loginuser@placementos.ai"


@pytest.mark.asyncio
async def test_login_invalid_password_fails(async_client: AsyncClient):
    """Test login with wrong password returns 401."""
    reg_payload = {
        "email": "wrongpass@placementos.ai",
        "password": "CorrectPassword123!",
        "full_name": "Wrong Pass User",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "wrongpass@placementos.ai",
        "password": "WrongPassword999!",
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_get_me_endpoint(async_client: AsyncClient):
    """Test /api/v1/auth/me returns current user info."""
    reg_payload = {
        "email": "me_user@placementos.ai",
        "password": "Password123!",
        "full_name": "Me User",
    }
    res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = res.json()["access_token"]

    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me_user@placementos.ai"
