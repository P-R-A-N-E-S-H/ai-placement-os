import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_roadmap_api_endpoints_workflow(async_client: AsyncClient):
    """Test full authenticated roadmap generation, retrieval, and task toggling via REST API."""
    # 1. Register candidate user
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "roadmap_api_user@example.com",
            "password": "Password123!",
            "full_name": "API Roadmap Tester",
        },
    )
    assert reg_res.status_code == 201
    auth_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 2. Generate roadmap for AI Engineer
    gen_res = await async_client.post(
        "/api/v1/learning/roadmaps/generate",
        headers=headers,
        json={
            "target_role": "AI Engineer",
            "weekly_hours": 15.0,
            "learning_style": "PRACTICAL",
        },
    )
    assert gen_res.status_code == 200
    roadmap_data = gen_res.json()
    assert roadmap_data["target_role"] in ["ai-engineer", "AI Engineer"]
    assert roadmap_data["status"] == "ACTIVE"
    assert len(roadmap_data["modules"]) >= 1
    roadmap_id = roadmap_data["id"]
    first_task = roadmap_data["modules"][0]["tasks"][0]
    task_id = first_task["id"]

    # 3. Retrieve active roadmap
    active_res = await async_client.get(
        "/api/v1/learning/roadmaps/active",
        headers=headers,
    )
    assert active_res.status_code == 200
    assert active_res.json()["id"] == roadmap_id

    # 4. Retrieve roadmap by ID
    by_id_res = await async_client.get(
        f"/api/v1/learning/roadmaps/{roadmap_id}",
        headers=headers,
    )
    assert by_id_res.status_code == 200
    assert by_id_res.json()["id"] == roadmap_id

    # 5. List all roadmaps
    list_res = await async_client.get(
        "/api/v1/learning/roadmaps",
        headers=headers,
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 6. Toggle task completion with evidence
    toggle_res = await async_client.patch(
        f"/api/v1/learning/roadmaps/tasks/{task_id}/toggle",
        headers=headers,
        json={
            "is_completed": True,
            "evidence_text": "Completed autonomous agent implementation lab with LangGraph StateGraph.",
            "evidence_source_id": "https://github.com/candidate/langgraph-agent",
        },
    )
    assert toggle_res.status_code == 200
    updated_task = toggle_res.json()
    assert updated_task["is_completed"] is True
    assert updated_task["evidence_text"] is not None

    # Check updated roadmap progress
    active_after = await async_client.get(
        "/api/v1/learning/roadmaps/active",
        headers=headers,
    )
    assert active_after.status_code == 200
    assert active_after.json()["completed_tasks"] == 1
    assert active_after.json()["progress_percentage"] > 0.0

    # 7. Untoggle task completion
    untoggle_res = await async_client.patch(
        f"/api/v1/learning/roadmaps/tasks/{task_id}/toggle",
        headers=headers,
        json={
            "is_completed": False,
        },
    )
    assert untoggle_res.status_code == 200
    assert untoggle_res.json()["is_completed"] is False

    active_untoggle = await async_client.get(
        "/api/v1/learning/roadmaps/active",
        headers=headers,
    )
    assert active_untoggle.status_code == 200
    assert active_untoggle.json()["completed_tasks"] == 0


@pytest.mark.asyncio
async def test_roadmap_api_unauthorized_access(async_client: AsyncClient):
    """Verify that unauthenticated requests to roadmap endpoints are rejected."""
    res = await async_client.get("/api/v1/learning/roadmaps/active")
    assert res.status_code in [401, 403]
