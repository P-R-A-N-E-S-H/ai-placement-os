import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_and_update_profile(async_client: AsyncClient):
    """Test updating user career profile and recalculating completion score."""
    reg_payload = {
        "email": "profileuser@placementos.ai",
        "password": "Password123!",
        "full_name": "Profile Candidate",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch initial profile
    get_res = await async_client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["full_name"] == "Profile Candidate"

    # 2. Update profile fields
    update_payload = {
        "headline": "Aspiring AI Engineer",
        "college": "MIT",
        "degree": "B.Tech",
        "branch": "Computer Science & AI",
        "graduation_year": 2026,
        "cgpa": 9.2,
        "target_roles": ["AI Engineer", "ML Engineer"],
        "preferred_locations": ["Bengaluru", "Remote"],
        "career_goal": "Lead research in Autonomous Agent Systems",
        "weekly_available_hours": 15,
        "github_url": "https://github.com/profileuser",
    }
    patch_res = await async_client.patch("/api/v1/profile", headers=headers, json=update_payload)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["headline"] == "Aspiring AI Engineer"
    assert data["cgpa"] == 9.2
    assert data["profile_completion"] > 15.0

    # 3. Check detailed completion breakdown
    comp_res = await async_client.get("/api/v1/profile/completion", headers=headers)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert "components" in comp_data
    assert comp_data["overall_completion"] > 0
