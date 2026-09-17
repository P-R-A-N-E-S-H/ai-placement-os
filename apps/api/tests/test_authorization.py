import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthenticated_profile_access_denied(async_client: AsyncClient):
    """Test accessing protected endpoints without Bearer token returns 401."""
    res = await async_client.get("/api/v1/profile")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_cross_user_isolation(async_client: AsyncClient):
    """Test User A cannot see or mutate User B's skills."""
    # Register User A
    user_a = await async_client.post("/api/v1/auth/register", json={
        "email": "user_a@placementos.ai",
        "password": "Password123!",
        "full_name": "User Alpha",
    })
    token_a = user_a.json()["access_token"]

    # Register User B
    user_b = await async_client.post("/api/v1/auth/register", json={
        "email": "user_b@placementos.ai",
        "password": "Password123!",
        "full_name": "User Beta",
    })
    token_b = user_b.json()["access_token"]

    # User A adds Python
    await async_client.post(
        "/api/v1/profile/skills",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"skill_name": "Python", "proficiency": 0.9},
    )

    # User B queries skills -> should have 0 skills
    skills_b_res = await async_client.get(
        "/api/v1/profile/skills",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert skills_b_res.status_code == 200
    assert len(skills_b_res.json()) == 0
