import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_demo_mode_endpoint(async_client: AsyncClient):
    """Test /api/v1/analytics/overview with demo=true returns seeded values."""
    res = await async_client.get("/api/v1/analytics/overview?demo=true")
    assert res.status_code == 200
    data = res.json()
    assert data["is_seeded_demo"] is True
    assert data["placement_readiness_score"] == 84.0
    assert len(data["top_skills"]) > 0


@pytest.mark.asyncio
async def test_analytics_authenticated_live_data(async_client: AsyncClient):
    """Test /api/v1/analytics/overview returns real user metrics."""
    reg_payload = {
        "email": "analyticsuser@placementos.ai",
        "password": "Password123!",
        "full_name": "Analytics Candidate",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add 2 skills
    await async_client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"skill_name": "Python", "proficiency": 0.9, "confidence": 0.85},
    )
    await async_client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"skill_name": "FastAPI", "proficiency": 0.8, "confidence": 0.75},
    )

    # Fetch live analytics
    res = await async_client.get("/api/v1/analytics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_seeded_demo"] is False
    assert data["total_skills_count"] == 2
    assert len(data["top_skills"]) == 2
    assert data["placement_readiness_score"] > 0
