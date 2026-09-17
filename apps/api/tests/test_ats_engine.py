import pytest
from app.schemas.resume import (
    ContactInfo,
    EducationItem,
    ParsedResumeData,
    ProjectItem,
)
from app.services.ats_engine import ATSEngine


def test_ats_engine_high_scoring_resume():
    """Test ATS evaluation on a well-structured quantified resume."""
    parsed = ParsedResumeData(
        contact_info=ContactInfo(
            name="Alex Parker",
            email="alex@placementos.ai",
            phone="+91 9876543210",
            github_url="https://github.com/alexparker",
            linkedin_url="https://linkedin.com/in/alexparker",
        ),
        education=[
            EducationItem(
                institution="MIT",
                degree="B.Tech",
                branch="Computer Science & AI",
                cgpa=9.2,
                graduation_year=2026,
            )
        ],
        projects=[
            ProjectItem(
                title="Distributed LLM Inference Engine",
                bullet_points=[
                    "Architected high-throughput inference engine in C++ and PyTorch reducing latency by 45%.",
                    "Optimized KV-cache quantization serving 2,500+ requests/sec with 99.9% uptime.",
                ],
            )
        ],
        skills=["Python", "C++", "PyTorch", "FastAPI", "Docker", "Kubernetes", "SQL", "Redis"],
    )

    raw_text = "Alex Parker alex@placementos.ai Architected high-throughput inference engine in C++ and PyTorch reducing latency by 45%."
    canonical_skills = ["Python", "C++", "PyTorch", "FastAPI", "Docker", "Kubernetes", "SQL", "Redis"]

    scorecard = ATSEngine.evaluate_resume(parsed, raw_text, canonical_skills)
    assert scorecard.overall_score >= 75.0
    assert scorecard.sub_scores["section_completeness"] == 100.0
    assert scorecard.sub_scores["quantification_coverage"] >= 80.0
    assert len(scorecard.strengths) > 0


def test_ats_engine_detects_missing_quantification():
    """Test ATS engine identifies lack of metrics and provides actionable advice."""
    parsed = ParsedResumeData(
        contact_info=ContactInfo(email="student@college.edu"),
        education=[],
        projects=[
            ProjectItem(
                title="Basic Web App",
                bullet_points=["worked on a website", "helped with backend"],
            )
        ],
        skills=["Python"],
    )

    scorecard = ATSEngine.evaluate_resume(parsed, "basic text", ["Python"])
    assert scorecard.overall_score < 60.0
    assert any("Quantify" in s for s in scorecard.actionable_improvements)
    assert any("passive phrases" in s for s in scorecard.actionable_improvements)
