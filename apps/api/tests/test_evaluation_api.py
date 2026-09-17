import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_evaluation_api_lifecycle(async_client: AsyncClient):
    """Test POST /api/v1/evaluation/run and GET /api/v1/evaluation/runs."""
    # 1. Run full suite
    resp = await async_client.post("/api/v1/evaluation/run", json={"benchmark_type": "ALL"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_benchmarks_executed"] == 3
    assert data["all_benchmarks_passed"] is True
    assert len(data["runs"]) == 3
    run_id = data["runs"][0]["id"]

    # 2. List runs
    list_resp = await async_client.get("/api/v1/evaluation/runs")
    assert list_resp.status_code == 200
    runs = list_resp.json()
    assert len(runs) >= 3

    # 3. Get specific run
    get_resp = await async_client.get(f"/api/v1/evaluation/runs/{run_id}")
    assert get_resp.status_code == 200
    run_data = get_resp.json()
    assert run_data["id"] == run_id
    assert run_data["status"] == "PASSED"

    # 4. Get non-existent run
    not_found = await async_client.get("/api/v1/evaluation/runs/non-existent-uuid")
    assert not_found.status_code == 404

