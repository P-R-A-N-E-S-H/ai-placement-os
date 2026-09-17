import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_logout_revokes_token(async_client: AsyncClient):
    """Test logout endpoint revokes the refresh token."""
    reg_payload = {
        "email": "logouttest@placementos.ai",
        "password": "Password123!",
        "full_name": "Logout Test User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    access_token = reg_res.json()["access_token"]
    refresh_token = reg_res.json()["refresh_token"]

    logout_res = await async_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 200

    # Attempting to refresh with the revoked token must fail
    ref_res = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 401


@pytest.mark.asyncio
async def test_logout_all_sessions(async_client: AsyncClient):
    """Test logout-all revokes all sessions."""
    reg_payload = {
        "email": "logoutall@placementos.ai",
        "password": "Password123!",
        "full_name": "Logout All User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    access_token = reg_res.json()["access_token"]
    refresh_token = reg_res.json()["refresh_token"]

    logout_all_res = await async_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_all_res.status_code == 200

    # Refresh must fail
    ref_res = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 401
