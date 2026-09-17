import math
import pytest
from app.services.job_embedding_service import JobEmbeddingService


def test_domain_semantic_vector_correlation():
    # 1. AI / ML Candidate Embedding
    v_ai_candidate = JobEmbeddingService.generate_candidate_embedding(
        target_role="AI Engineer",
        skills=["Python", "PyTorch", "LangChain", "LangGraph", "RAG"],
        projects_text="Built autonomous multi-agent systems and vector search with transformer models.",
    )

    # 2. Machine Learning Job Embedding (Semantically Aligned)
    v_ai_job = JobEmbeddingService.generate_job_embedding(
        title="Associate AI / ML Engineer",
        company="OpenAI Partner Labs",
        location="Bengaluru",
        skills=["Python", "PyTorch", "Transformers", "Large Language Models", "FastAPI"],
        description="Design retrieval augmented generation pipelines and fine-tune foundation models.",
    )

    # 3. Frontend Web Developer Job Embedding (Semantically Distant)
    v_frontend_job = JobEmbeddingService.generate_job_embedding(
        title="Senior Frontend UI Engineer",
        company="Design Studios",
        location="Berlin",
        skills=["React", "Next.js", "TypeScript", "Tailwind CSS", "HTML", "CSS"],
        description="Craft pixel-perfect responsive web components and browser state management.",
    )

    # Verify unit norms
    norm_cand = math.sqrt(sum(x * x for x in v_ai_candidate))
    norm_ai_job = math.sqrt(sum(x * x for x in v_ai_job))
    norm_fe_job = math.sqrt(sum(x * x for x in v_frontend_job))

    assert pytest.approx(norm_cand, rel=1e-3) == 1.0
    assert pytest.approx(norm_ai_job, rel=1e-3) == 1.0
    assert pytest.approx(norm_fe_job, rel=1e-3) == 1.0

    # Semantic similarity: AI Candidate vs AI Job must be significantly higher than AI Candidate vs Frontend Job
    sim_ai = JobEmbeddingService.cosine_similarity(v_ai_candidate, v_ai_job)
    sim_fe = JobEmbeddingService.cosine_similarity(v_ai_candidate, v_frontend_job)

    assert sim_ai > 0.55
    assert sim_fe < 0.35
    assert sim_ai - sim_fe > 0.25  # Meaningful semantic separation
