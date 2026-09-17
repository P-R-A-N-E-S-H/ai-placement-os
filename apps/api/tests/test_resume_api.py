import io
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.models.resume import Resume
from app.models.skill import SkillEvidence, UserSkill


SAMPLE_RESUME_TEXT = """
PRANESH M
Email: pranesh@placementos.ai
Phone: +91 9876543210
GitHub: https://github.com/pranesh-ai
LinkedIn: https://linkedin.com/in/pranesh-m

EDUCATION
Bachelor of Technology in Computer Science & AI
National Institute of Technology, CGPA: 9.15, Graduating: 2026

SKILLS
Languages & Frameworks: Python, TypeScript, React, Next.js, FastAPI, Node.js, PyTorch
Databases & Cloud: PostgreSQL, Redis, Docker, Kubernetes, AWS, MongoDB
AI & Core: LLM Orchestration, LangChain, LangGraph, Vector Databases, Data Structures & Algorithms

PROJECTS
Autonomous Multi-Agent Career Intelligence Platform
• Architected scalable FastAPI backend orchestrating 12 autonomous career agents with Redis message queue, handling 1,500+ requests/second.
• Engineered deterministic ATS parsing pipeline with regex tokenization and canonical skill extraction, achieving 98.4% precision on 500+ student resumes.
• Integrated PostgreSQL vector embeddings with pgvector for sub-50ms semantic job-resume matching across 10,000+ real-time listings.

High-Throughput Distributed Microservices Engine
• Implemented robust Dockerized microservices deployed on Kubernetes with automated CI/CD pipeline, reducing deployment latency by 60%.
• Designed optimized SQL query indices in PostgreSQL, decreasing database p99 query latency from 240ms to 18ms.
"""


async def get_test_auth_headers(async_client: AsyncClient, email: str = "pranesh@placementos.ai") -> dict:
    reg_payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Pranesh M",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_resume_upload_and_analysis(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client)

    file_content = SAMPLE_RESUME_TEXT.encode("utf-8")
    files = {
        "file": ("pranesh_resume.txt", io.BytesIO(file_content), "text/plain")
    }

    response = await async_client.post(
        "/api/v1/resumes/upload",
        files=files,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "pranesh_resume.txt"
    assert data["file_type"] == "txt"
    assert data["ats_score"] > 60.0
    assert "ats_feedback" in data
    assert data["ats_feedback"]["sub_scores"]["section_completeness"] > 0
    assert data["ats_feedback"]["sub_scores"]["quantification_coverage"] > 0
    assert data["ats_feedback"]["sub_scores"]["skill_density"] > 0
    assert len(data["parsed_data"]["skills"]) > 0

    # Verify canonical skills mapped
    extracted_skills = data["parsed_data"]["skills"]
    assert "Python" in extracted_skills or "FastAPI" in extracted_skills or "PostgreSQL" in extracted_skills

    resume_id = data["id"]

    # Verify profile endpoint shows updated data synced from resume
    profile_res = await async_client.get("/api/v1/profile", headers=auth_headers)
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["cgpa"] == 9.15
    assert profile_data["graduation_year"] == 2026
    assert profile_data["github_url"] == "https://github.com/pranesh-ai"

    # Verify skills list endpoint shows synced skills
    skills_res = await async_client.get("/api/v1/profile/skills", headers=auth_headers)
    assert skills_res.status_code == 200
    user_skills = skills_res.json()
    assert len(user_skills) > 0


@pytest.mark.asyncio
async def test_list_and_get_resumes(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client, "candidate2@placementos.ai")

    file_content = SAMPLE_RESUME_TEXT.encode("utf-8")
    files = {
        "file": ("candidate_resume.txt", io.BytesIO(file_content), "text/plain")
    }
    upload_res = await async_client.post(
        "/api/v1/resumes/upload",
        files=files,
        headers=auth_headers,
    )
    assert upload_res.status_code == 201
    resume_id = upload_res.json()["id"]

    # List
    list_res = await async_client.get("/api/v1/resumes", headers=auth_headers)
    assert list_res.status_code == 200
    resumes = list_res.json()
    assert len(resumes) >= 1
    assert any(r["id"] == resume_id for r in resumes)

    # Get by ID
    get_res = await async_client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == resume_id
    assert get_res.json()["file_name"] == "candidate_resume.txt"


@pytest.mark.asyncio
async def test_delete_resume(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client, "candidate3@placementos.ai")

    file_content = SAMPLE_RESUME_TEXT.encode("utf-8")
    files = {
        "file": ("temp_resume.txt", io.BytesIO(file_content), "text/plain")
    }
    upload_res = await async_client.post(
        "/api/v1/resumes/upload",
        files=files,
        headers=auth_headers,
    )
    resume_id = upload_res.json()["id"]

    # Delete
    del_res = await async_client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # Verify 404 after deletion
    get_res = await async_client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_cross_user_resume_isolation(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client, "user1@placementos.ai")

    # User 1 uploads
    file_content = SAMPLE_RESUME_TEXT.encode("utf-8")
    files = {
        "file": ("user1_resume.txt", io.BytesIO(file_content), "text/plain")
    }
    upload_res = await async_client.post(
        "/api/v1/resumes/upload",
        files=files,
        headers=auth_headers,
    )
    user1_resume_id = upload_res.json()["id"]

    # Register user 2
    user2_headers = await get_test_auth_headers(async_client, "user2@placementos.ai")

    # User 2 tries to access user 1's resume -> 404
    get_res = await async_client.get(f"/api/v1/resumes/{user1_resume_id}", headers=user2_headers)
    assert get_res.status_code == 404

    # User 2 tries to delete user 1's resume -> 404
    del_res = await async_client.delete(f"/api/v1/resumes/{user1_resume_id}", headers=user2_headers)
    assert del_res.status_code == 404
