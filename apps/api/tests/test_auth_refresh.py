import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_refresh_token_rotation_success(async_client: AsyncClient):
    """Test refreshing token returns a brand new access and refresh token pair."""
    reg_payload = {
        "email": "refreshtest@placementos.ai",
        "password": "Password123!",
        "full_name": "Refresh Test User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    old_refresh = reg_res.json()["refresh_token"]

    refresh_res = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    new_refresh = data["refresh_token"]
    assert new_refresh != old_refresh
    assert "access_token" in data


@pytest.mark.asyncio
async def test_revoked_token_reuse_rejected(async_client: AsyncClient):
    """Test using an already-used refresh token is detected and rejected."""
    reg_payload = {
        "email": "reusetest@placementos.ai",
        "password": "Password123!",
        "full_name": "Reuse Test User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    first_refresh = reg_res.json()["refresh_token"]

    # First rotation: succeeds
    res1 = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
    assert res1.status_code == 200

    # Second rotation with same old token: must fail with reuse detection
    res2 = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
    assert res2.status_code == 401
