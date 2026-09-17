import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dsa_api_full_workflow(async_client: AsyncClient):
    """Test full DSA API workflow: list problems, get detail, run test cases, submit, view submissions and stats."""
    # 1. Register candidate user
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "dsa_api_user@example.com",
            "password": "Password123!",
            "full_name": "API DSA Tester",
        },
    )
    assert reg_res.status_code == 201
    auth_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 2. List problems (public or authenticated)
    list_res = await async_client.get("/api/v1/dsa/problems", headers=headers)
    assert list_res.status_code == 200
    problems = list_res.json()
    assert len(problems) >= 8
    two_sum = next(p for p in problems if p["slug"] == "two-sum")
    assert two_sum["is_solved"] is False

    # 3. Get problem details
    detail_res = await async_client.get(f"/api/v1/dsa/problems/{two_sum['slug']}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "Two Sum"
    assert len(detail["test_cases"]) > 0
    assert "python" in detail["starter_code"]

    # 4. Run code on sample test cases
    two_sum_code = (
        "class Solution:\n"
        "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
        "        lookup = {}\n"
        "        for i, val in enumerate(nums):\n"
        "            diff = target - val\n"
        "            if diff in lookup:\n"
        "                return [lookup[diff], i]\n"
        "            lookup[val] = i\n"
        "        return []\n"
    )
    run_res = await async_client.post(
        f"/api/v1/dsa/problems/{two_sum['slug']}/run",
        json={"language": "python", "code": two_sum_code},
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["status"] == "ACCEPTED"
    assert run_data["passed_count"] == run_data["total_count"]

    # 5. Submit code
    submit_res = await async_client.post(
        f"/api/v1/dsa/problems/{two_sum['slug']}/submit",
        headers=headers,
        json={"language": "python", "code": two_sum_code},
    )
    assert submit_res.status_code == 201
    sub_data = submit_res.json()
    assert sub_data["status"] == "ACCEPTED"
    assert sub_data["passed_test_cases"] == sub_data["total_test_cases"]
    assert sub_data["ai_feedback"] is not None

    # 6. List submissions
    subs_res = await async_client.get("/api/v1/dsa/submissions", headers=headers)
    assert subs_res.status_code == 200
    assert len(subs_res.json()) >= 1

    # 7. Get candidate DSA stats
    stats_res = await async_client.get("/api/v1/dsa/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_solved"] == 1
    assert stats["easy_solved"] == 1
    assert stats["overall_accuracy_percentage"] == 100.0


@pytest.mark.asyncio
async def test_dsa_api_unauthenticated_submit_fails(async_client: AsyncClient):
    """Verify unauthenticated submission is rejected."""
    res = await async_client.post(
        "/api/v1/dsa/problems/two-sum/submit",
        json={"language": "python", "code": "pass"},
    )
    assert res.status_code in [401, 403]
