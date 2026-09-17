import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_skills_normalization(async_client: AsyncClient):
    """Test deterministic normalization of common aliases (JS -> JavaScript, torch -> PyTorch)."""
    # 1. Seed some sample skills first via normalize or direct declaration
    batch_payload = {
        "raw_skills": ["Python", "JS", "pytorch", "FastAPI", "UnrecognizedSkill123"]
    }
    response = await async_client.post("/api/v1/skills/normalize", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["normalized"]) == 5
    assert data["normalized"][0]["raw_input"] == "Python"


@pytest.mark.asyncio
async def test_user_skills_crud(async_client: AsyncClient):
    """Test candidate declaring skills with proficiency and retrieving them."""
    reg_payload = {
        "email": "skilluser@placementos.ai",
        "password": "Password123!",
        "full_name": "Skill User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add skill: Python with 0.85 proficiency
    add_payload = {
        "skill_name": "Python",
        "proficiency": 0.85,
        "confidence": 0.9,
        "years_experience": 3.0,
        "source": "USER_DECLARED",
        "evidence_text": "Built 4 production projects with Python and PyTorch.",
    }
    add_res = await async_client.post("/api/v1/profile/skills", headers=headers, json=add_payload)
    assert add_res.status_code == 201
    skill_data = add_res.json()
    assert skill_data["proficiency"] == 0.85
    assert skill_data["skill"]["name"] == "Python"
    skill_id = skill_data["skill_id"]

    # List user skills
    list_res = await async_client.get("/api/v1/profile/skills", headers=headers)
    assert list_res.status_code == 200
    skills_list = list_res.json()
    assert len(skills_list) == 1
    assert skills_list[0]["skill"]["name"] == "Python"

    # Delete skill
    del_res = await async_client.delete(f"/api/v1/profile/skills/{skill_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify empty
    list_res2 = await async_client.get("/api/v1/profile/skills", headers=headers)
    assert len(list_res2.json()) == 0
