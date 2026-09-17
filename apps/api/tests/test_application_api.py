import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_application_api_full_workflow(async_client: AsyncClient):
    """Verify application tracking endpoints via REST API."""
    # Register candidate user
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "pipeline_user@example.com",
            "password": "Password123!",
            "full_name": "Pipeline Tracker Tester",
        },
    )
    assert reg_res.status_code == 201
    auth_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Create Application
    create_res = await async_client.post(
        "/api/v1/applications",
        headers=headers,
        json={
            "company_name": "Meta",
            "job_title": "Production Engineer",
            "location": "Menlo Park, CA",
            "stage": "APPLIED",
            "match_score": 91.0,
            "notes": "Referred by university alumni",
        },
    )
    assert create_res.status_code == 201
    app_data = create_res.json()
    app_id = app_data["id"]
    assert app_data["company_name"] == "Meta"
    assert app_data["stage"] == "APPLIED"

    # 2. List Applications
    list_res = await async_client.get("/api/v1/applications", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Update stage to OA_SCHEDULED
    patch_res = await async_client.patch(
        f"/api/v1/applications/{app_id}",
        headers=headers,
        json={"stage": "OA_SCHEDULED", "notes": "CoderPad test scheduled for next Tuesday"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["stage"] == "OA_SCHEDULED"

    # 4. Get Pipeline Statistics
    stats_res = await async_client.get("/api/v1/applications/stats", headers=headers)
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert stats_data["total_applications"] >= 1
    assert stats_data["oa_scheduled_count"] >= 1

    # 5. Delete Application
    del_res = await async_client.delete(f"/api/v1/applications/{app_id}", headers=headers)
    assert del_res.status_code == 204
