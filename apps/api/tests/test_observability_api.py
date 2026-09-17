import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_observability_and_velocity_api(async_client: AsyncClient):
    """Verify platform observability telemetry and velocity trajectory endpoints."""
    # 1. Observability Health endpoint
    obs_res = await async_client.get("/api/v1/analytics/observability")
    assert obs_res.status_code == 200
    obs_data = obs_res.json()
    assert obs_data["status"] == "OPERATIONAL"
    assert obs_data["database_status"] == "CONNECTED"
    assert len(obs_data["subsystems"]) >= 6
    assert any(s["name"] == "Career Digital Twin" for s in obs_data["subsystems"])
    assert any(s["name"] == "Hybrid RAG & Knowledge Graph" for s in obs_data["subsystems"])

    # 2. Velocity Trajectory endpoint
    vel_res = await async_client.get("/api/v1/analytics/velocity?target_role=AI%20Engineer")
    assert vel_res.status_code == 200
    vel_data = vel_res.json()
    assert vel_data["target_role"] == "AI Engineer"
    assert len(vel_data["trajectory_points"]) >= 5
    assert vel_data["trajectory_points"][-1]["readiness_score"] >= 90.0
