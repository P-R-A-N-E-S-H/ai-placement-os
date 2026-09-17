import pytest
from httpx import AsyncClient
from app.models.job import Job, JobSkill


@pytest.mark.asyncio
async def test_get_role_benchmarks_and_prerequisite_graph_public(async_client: AsyncClient):
    # 1. Role Benchmarks
    bench_res = await async_client.get("/api/v1/skills/roles/benchmarks")
    assert bench_res.status_code == 200
    benchmarks = bench_res.json()
    assert len(benchmarks) >= 5
    slugs = [b["role_slug"] for b in benchmarks]
    assert "ai-engineer" in slugs
    assert "backend-engineer" in slugs

    # 2. Prerequisite Graph
    graph_res = await async_client.get("/api/v1/skills/prerequisites/graph")
    assert graph_res.status_code == 200
    graph = graph_res.json()
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0


@pytest.mark.asyncio
async def test_role_skill_gap_analysis_authenticated(async_client: AsyncClient):
    # 1. Register candidate
    email = "gap_candidate@example.com"
    pwd = "Password123!"
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pwd, "full_name": "Gap Candidate"},
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed some user skills (Python=0.9, FastAPI=0.7)
    await async_client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"skill_name": "Python", "proficiency": 0.9, "confidence": 0.9, "source": "RESUME"},
    )
    await async_client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"skill_name": "FastAPI", "proficiency": 0.7, "confidence": 0.8, "source": "PROJECT"},
    )

    # 3. Analyze against AI Engineer Role
    gap_res = await async_client.post(
        "/api/v1/skills/gap-analysis/role",
        headers=headers,
        json={"target_role": "ai-engineer", "weekly_hours": 20.0},
    )
    assert gap_res.status_code == 200
    data = gap_res.json()

    assert data["target_type"] == "ROLE"
    assert data["target_id"] == "ai-engineer"
    assert data["readiness_score"] > 0.0
    assert data["total_skills_required"] > 0
    assert data["total_estimated_hours"] > 0.0
    assert data["estimated_weeks"] > 0.0
    assert len(data["gap_items"]) > 0
    assert len(data["learning_pathway"]) > 0

    # Validate Python is marked as SATISFIED
    python_item = next(g for g in data["gap_items"] if g["slug"] == "python")
    assert python_item["gap_type"] == "SATISFIED"
    assert python_item["current_proficiency"] == 0.9

    # 4. Check GET /api/v1/skills/gap-analysis/latest
    latest_res = await async_client.get("/api/v1/skills/gap-analysis/latest", headers=headers)
    assert latest_res.status_code == 200
    latest_data = latest_res.json()
    assert latest_data["id"] == data["id"]
    assert latest_data["target_id"] == "ai-engineer"


@pytest.mark.asyncio
async def test_job_skill_gap_analysis(async_client: AsyncClient):
    # 1. Register candidate
    email = "job_gap_user@example.com"
    pwd = "Password123!"
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pwd, "full_name": "Job Gap Candidate"},
    )
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ingest jobs first
    await async_client.post("/api/v1/jobs/ingest", headers=headers)

    # 3. Get first job
    jobs_res = await async_client.get("/api/v1/jobs?page=1&page_size=1")
    assert jobs_res.status_code == 200
    items = jobs_res.json()["items"]
    assert len(items) > 0
    job_id = items[0]["id"]

    # 4. Analyze gap against job
    job_gap_res = await async_client.post(
        f"/api/v1/skills/gap-analysis/job/{job_id}",
        headers=headers,
        json={"weekly_hours": 15.0},
    )
    assert job_gap_res.status_code == 200
    job_gap_data = job_gap_res.json()
    assert job_gap_data["target_type"] == "JOB"
    assert job_gap_data["target_id"] == job_id
    assert len(job_gap_data["gap_items"]) > 0


@pytest.mark.asyncio
async def test_unauthenticated_access_denied(async_client: AsyncClient):
    res = await async_client.post("/api/v1/skills/gap-analysis/role", json={"target_role": "ai-engineer"})
    assert res.status_code == 401
