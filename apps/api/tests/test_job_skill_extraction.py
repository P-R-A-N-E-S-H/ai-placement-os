import math
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.services.job_embedding_service import JobEmbeddingService
from app.services.job_skill_extractor import JobSkillExtractor


@pytest.mark.asyncio
async def test_job_skill_extraction_and_classification(async_client):
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as session:
        title = "Senior AI Engineer (Python & PyTorch)"
        description = """
        Requirements:
        - Must have deep experience in Python, PyTorch, and PostgreSQL.
        - Solid understanding of Data Structures & Algorithms.

        Preferred Qualifications:
        - Nice to have: Docker, Kubernetes, and AWS deployment experience.
        """
        raw_tags = ["Python", "PyTorch", "AI"]

        skills = await JobSkillExtractor.extract_skills_for_job(
            db=session,
            title=title,
            description=description,
            raw_tags=raw_tags,
        )

        skill_names = {s.skill_name: s for s in skills}
        assert "Python" in skill_names
        assert "PyTorch" in skill_names
        assert "PostgreSQL" in skill_names

        # Python in title -> is_required=True, importance=1.0
        assert skill_names["Python"].is_required is True
        assert skill_names["Python"].importance_score == 1.0

        # Docker in Nice to have -> is_required=False
        if "Docker" in skill_names:
            assert skill_names["Docker"].is_required is False


def test_job_embedding_generation():
    embedding = JobEmbeddingService.generate_job_embedding(
        title="AI Engineer",
        company="OpenAI",
        location="San Francisco",
        skills=["Python", "PyTorch", "LangChain"],
        description="Build LLM agent systems.",
    )

    assert len(embedding) == 128
    # Test L2 unit norm
    norm = math.sqrt(sum(x * x for x in embedding))
    assert pytest.approx(norm, rel=1e-3) == 1.0
