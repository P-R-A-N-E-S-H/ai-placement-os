import io
import pytest
from httpx import AsyncClient


SAMPLE_AI_RESUME = """
PRANESH M
Email: candidate_match@placementos.ai
Phone: +91 9876543210
GitHub: https://github.com/pranesh-ai

EDUCATION
Bachelor of Technology in Computer Science & AI
National Institute of Technology, CGPA: 9.15, Graduating: 2026

SKILLS
Python, PyTorch, LangGraph, LangChain, FastAPI, PostgreSQL, Redis, Docker, System Design

PROJECTS
Autonomous Multi-Agent Career Platform
• Architected scalable FastAPI backend orchestrating 12 autonomous career agents with Redis message queue, handling 1,500+ requests/second.
• Engineered deterministic ATS parsing pipeline with regex tokenization and canonical skill extraction.
"""


async def get_test_auth_headers(async_client: AsyncClient, email: str = "matchuser@placementos.ai") -> dict:
    reg_payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Match Candidate",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_calculate_single_job_match_api(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client)

    # 1. Ingest curated jobs
    await async_client.post(
        "/api/v1/jobs/ingest",
        json={"source_names": ["curated_placement"]},
        headers=auth_headers,
    )

    # 2. Upload resume to populate Career Twin skills & academics
    file_content = SAMPLE_AI_RESUME.encode("utf-8")
    files = {"file": ("resume.txt", io.BytesIO(file_content), "text/plain")}
    await async_client.post("/api/v1/resumes/upload", files=files, headers=auth_headers)

    # 3. Get job ID for OpenAI AI Engineer role
    jobs_res = await async_client.get("/api/v1/jobs?search=OpenAI")
    assert jobs_res.status_code == 200
    ai_job = next(j for j in jobs_res.json()["items"] if "OpenAI" in j["company"])
    job_id = ai_job["id"]

    # 4. Calculate Match
    match_res = await async_client.post(f"/api/v1/matches/calculate/{job_id}", headers=auth_headers)
    assert match_res.status_code == 200
    match_data = match_res.json()

    assert match_data["overall_score"] > 60.0
    assert match_data["skill_score"] > 0
    assert match_data["experience_score"] > 0
    assert match_data["education_score"] > 0
    assert match_data["semantic_score"] > 0
    assert match_data["evidence_score"] > 0
    assert match_data["preference_score"] > 0

    assert len(match_data["matched_required_skills"]) > 0
    assert any(sk in match_data["matched_required_skills"] for sk in ["Python", "PyTorch", "FastAPI", "PostgreSQL", "System Design"])

    assert "breakdown" in match_data
    assert "explanation" in match_data
    assert len(match_data["explanation"]["strengths"]) > 0


@pytest.mark.asyncio
async def test_batch_match_ranking_api(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client, "batchuser@placementos.ai")

    # Ingest & upload resume
    await async_client.post(
        "/api/v1/jobs/ingest",
        json={"source_names": ["curated_placement"]},
        headers=auth_headers,
    )
    file_content = SAMPLE_AI_RESUME.encode("utf-8")
    files = {"file": ("resume.txt", io.BytesIO(file_content), "text/plain")}
    await async_client.post("/api/v1/resumes/upload", files=files, headers=auth_headers)

    # Batch match
    batch_res = await async_client.post("/api/v1/matches/batch?limit=10", headers=auth_headers)
    assert batch_res.status_code == 200
    batch_data = batch_res.json()

    assert batch_data["total_evaluated"] >= 4
    matches = batch_data["matches"]
    assert len(matches) >= 4

    # Verify sorted descending by overall_score
    scores = [m["overall_score"] for m in matches]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_list_matches_and_filter_api(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client, "listuser@placementos.ai")

    # Ingest, resume, and batch match
    await async_client.post(
        "/api/v1/jobs/ingest",
        json={"source_names": ["curated_placement"]},
        headers=auth_headers,
    )
    file_content = SAMPLE_AI_RESUME.encode("utf-8")
    files = {"file": ("resume.txt", io.BytesIO(file_content), "text/plain")}
    await async_client.post("/api/v1/resumes/upload", files=files, headers=auth_headers)
    await async_client.post("/api/v1/matches/batch", headers=auth_headers)

    # List all matches
    list_res = await async_client.get("/api/v1/matches", headers=auth_headers)
    assert list_res.status_code == 200
    all_matches = list_res.json()
    assert len(all_matches) > 0

    # Filter with min_score
    filtered_res = await async_client.get("/api/v1/matches?min_score=70", headers=auth_headers)
    assert filtered_res.status_code == 200
    filtered = filtered_res.json()
    for m in filtered:
        assert m["overall_score"] >= 70.0
