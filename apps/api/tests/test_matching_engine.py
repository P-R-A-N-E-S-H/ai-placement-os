import pytest
from app.models.job import Job, JobSkill
from app.models.profile import UserProfile
from app.models.skill import Skill, SkillEvidence, UserSkill
from app.services.matching_engine import MatchingEngine


def test_matching_engine_skill_coverage():
    # Setup mock job skills
    s_python = Skill(name="Python", slug="python", category="PROGRAMMING_LANGUAGE")
    s_pytorch = Skill(name="PyTorch", slug="pytorch", category="AI_ML")
    s_docker = Skill(name="Docker", slug="docker", category="DEVOPS")

    js_python = JobSkill(skill=s_python, is_required=True, importance_score=1.0)
    js_pytorch = JobSkill(skill=s_pytorch, is_required=True, importance_score=1.0)
    js_docker = JobSkill(skill=s_docker, is_required=False, importance_score=0.6)

    # Candidate has Python & PyTorch (all required), lacks Docker (preferred)
    cand_skills = {"Python", "PyTorch", "FastAPI"}
    job_skills = [js_python, js_pytorch, js_docker]

    (
        skill_score,
        matched_req,
        missing_req,
        matched_pref,
        missing_pref,
        req_ratio,
        pref_ratio,
    ) = MatchingEngine.compute_skill_match(cand_skills, job_skills)

    assert skill_score == 75.0  # 100% of required (0.75) + 0% of preferred (0.0)
    assert matched_req == ["Python", "PyTorch"]
    assert missing_req == []
    assert matched_pref == []
    assert missing_pref == ["Docker"]
    assert req_ratio == 1.0
    assert pref_ratio == 0.0


def test_matching_engine_experience_and_education():
    profile = UserProfile(
        user_id="test_user",
        degree="B.Tech",
        branch="Computer Science & Engineering",
        cgpa=8.8,
        experience_level="intermediate",
    )

    job_entry = Job(
        title="Associate AI Engineer",
        slug="associate-ai-engineer",
        company="Tech Corp",
        location="Remote",
        min_experience_years=1.0,
        max_experience_years=2.0,
        description="Engineering role",
        fingerprint="fp123",
        source="curated",
        source_url="https://example.com/job1",
    )

    exp_score = MatchingEngine.compute_experience_fit(profile, job_entry, project_count=3)
    edu_score = MatchingEngine.compute_education_fit(profile, job_entry)

    assert exp_score == 100.0  # Intermediate (~2.0 yrs >= 1.0)
    assert edu_score >= 90.0  # B.Tech (40) + CS (30) + 8.8 CGPA (30) = 100.0


def test_matching_engine_overall_score_and_explanation():
    profile = UserProfile(
        user_id="test_user",
        degree="B.Tech",
        branch="Artificial Intelligence",
        cgpa=9.1,
        experience_level="entry_level",
        target_roles=["AI Engineer"],
        remote_preference=True,
    )

    s_python = Skill(name="Python", slug="python", category="PROGRAMMING_LANGUAGE")
    s_docker = Skill(name="Docker", slug="docker", category="DEVOPS")

    us_python = UserSkill(
        user_id="test_user",
        skill_id="1",
        skill=s_python,
        proficiency=0.85,
        evidence=[SkillEvidence(evidence_text="Built autonomous agents in Python.")],
    )

    js_python = JobSkill(skill=s_python, is_required=True, importance_score=1.0)
    js_docker = JobSkill(skill=s_docker, is_required=True, importance_score=1.0)

    job = Job(
        title="AI Engineer",
        slug="ai-engineer-1",
        company="OpenAI Labs",
        location="Bengaluru",
        location_type="HYBRID",
        min_experience_years=0.0,
        description="AI systems development",
        fingerprint="fp456",
        source="curated",
        source_url="https://example.com/ai-job",
        job_skills=[js_python, js_docker],
        embedding=[0.1] * 128,
    )

    (
        overall,
        skill_s,
        exp_s,
        edu_s,
        sem_s,
        evid_s,
        pref_s,
        matched_req,
        missing_req,
        matched_pref,
        missing_pref,
        breakdown,
        explanation,
    ) = MatchingEngine.evaluate_match(
        profile=profile,
        user_skills=[us_python],
        candidate_embedding=[0.1] * 128,
        project_count=2,
        job=job,
    )

    assert 0.0 <= overall <= 100.0
    assert "Python" in matched_req
    assert "Docker" in missing_req
    assert len(explanation.gaps) > 0
    assert any("Docker" in g for g in explanation.gaps)
    assert len(explanation.recommendations) > 0
