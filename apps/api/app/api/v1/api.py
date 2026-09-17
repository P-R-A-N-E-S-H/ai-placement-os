from fastapi import APIRouter
from app.api.v1.endpoints import (
    analytics,
    applications,
    auth,
    dsa,
    evaluation,
    health,
    interviews,
    jobs,
    matches,
    orchestrator,
    profile,
    rag,
    resumes,
    roadmaps,
    security,
    skill_gaps,
    skills,
)

api_router = APIRouter()

# Core System & Health
api_router.include_router(health.router, tags=["System & Health"])

# Authentication & Digital Twin
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(skills.router)
api_router.include_router(analytics.router)
api_router.include_router(applications.router)

# Phase 3: Resume Intelligence
api_router.include_router(resumes.router)

# Phase 4: Job Discovery & Ingestion
api_router.include_router(jobs.router)

# Phase 5: Hybrid Job-Resume Matching Engine
api_router.include_router(matches.router)

# Phase 6: Skill Gap Analysis & Prerequisite DAG
api_router.include_router(skill_gaps.router)

# Phase 7: Adaptive Learning Roadmap Generator
api_router.include_router(roadmaps.router)

# Phase 8: DSA Preparation Engine & Sandbox
api_router.include_router(dsa.router)

# Phase 9: Mock Interview Simulation Agent
api_router.include_router(interviews.router)

# Phase 10: Hybrid RAG & Knowledge Graph
api_router.include_router(rag.router, prefix="/rag", tags=["Hybrid RAG & Knowledge Graph"])

# Phase 11: LangGraph Multi-Agent Orchestrator
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["Multi-Agent Orchestrator"])

# Phase 13: Security Hardening & Guardrails
api_router.include_router(security.router)

# Phase 14: Automated Evaluation Framework & Benchmark Suites
api_router.include_router(evaluation.router)


