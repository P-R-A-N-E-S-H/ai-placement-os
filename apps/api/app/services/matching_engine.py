import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.models.job import Job, JobSkill
from app.models.profile import UserProfile
from app.models.skill import SkillEvidence, UserSkill
from app.schemas.match import MatchBreakdown, MatchExplanation
from app.services.job_embedding_service import JobEmbeddingService


class MatchingEngine:
    """
    Deterministic 6-Factor Hybrid Job-Resume Matching Engine.
    Configurable weights and explainable match scorecard.
    """

    # Configurable weights (Sum = 1.0)
    WEIGHT_SKILL = 0.30
    WEIGHT_EXPERIENCE = 0.20
    WEIGHT_EDUCATION = 0.10
    WEIGHT_SEMANTIC = 0.15
    WEIGHT_EVIDENCE = 0.15
    WEIGHT_PREFERENCE = 0.10

    @classmethod
    def compute_skill_match(
        cls,
        candidate_skills: Set[str],
        job_skills: List[JobSkill],
    ) -> Tuple[float, List[str], List[str], List[str], List[str], float, float]:
        """
        Evaluate deterministic required vs preferred canonical skill overlap.
        """
        required_job_skills = [
            js.skill.name for js in job_skills if js.is_required and js.skill
        ]
        preferred_job_skills = [
            js.skill.name for js in job_skills if not js.is_required and js.skill
        ]

        candidate_lower = {s.lower() for s in candidate_skills}

        matched_required: List[str] = []
        missing_required: List[str] = []
        for req in required_job_skills:
            if req.lower() in candidate_lower:
                matched_required.append(req)
            else:
                missing_required.append(req)

        matched_preferred: List[str] = []
        missing_preferred: List[str] = []
        for pref in preferred_job_skills:
            if pref.lower() in candidate_lower:
                matched_preferred.append(pref)
            else:
                missing_preferred.append(pref)

        req_total = max(1, len(required_job_skills))
        req_ratio = len(matched_required) / req_total

        if preferred_job_skills:
            pref_ratio = len(matched_preferred) / len(preferred_job_skills)
            skill_score = (0.75 * req_ratio + 0.25 * pref_ratio) * 100.0
        else:
            pref_ratio = 1.0
            skill_score = req_ratio * 100.0

        return (
            round(min(100.0, max(0.0, skill_score)), 1),
            matched_required,
            missing_required,
            matched_preferred,
            missing_preferred,
            round(req_ratio, 3),
            round(pref_ratio, 3),
        )

    @classmethod
    def compute_experience_fit(
        cls,
        profile: Optional[UserProfile],
        job: Job,
        project_count: int,
    ) -> float:
        """
        Assess experience alignment (years, internships, project tenure).
        """
        # Map experience_level to estimated years
        level_map = {
            "entry_level": 0.5,
            "intermediate": 2.0,
            "mid_level": 3.0,
            "senior": 5.0,
        }
        cand_exp = 0.5
        if profile:
            cand_exp = level_map.get(profile.experience_level, 0.5)

        min_exp = job.min_experience_years or 0.0
        max_exp = job.max_experience_years

        if cand_exp >= min_exp:
            if max_exp and cand_exp > max_exp + 3.0:
                # Slight overqualification taper
                return 85.0
            return 100.0

        # If below min_experience, scale with credit for portfolio projects
        gap = min_exp - cand_exp
        base = max(20.0, (cand_exp / max(1.0, min_exp)) * 80.0)
        project_bonus = min(20.0, project_count * 5.0)
        return round(min(100.0, base + project_bonus), 1)

    @classmethod
    def compute_education_fit(
        cls,
        profile: Optional[UserProfile],
        job: Job,
    ) -> float:
        """
        Evaluate degree level, branch relevance, and academic CGPA benchmarks.
        """
        if not profile:
            return 70.0

        score = 0.0

        # Degree (40 pts)
        degree = (profile.degree or "B.Tech").lower()
        if any(d in degree for d in ["b.tech", "m.tech", "b.e", "b.sc", "mca", "bachelor", "master"]):
            score += 40.0
        else:
            score += 25.0

        # Branch (30 pts)
        branch = (profile.branch or "Computer Science").lower()
        if any(b in branch for b in ["computer", "ai", "artificial", "data", "software", "information", "it"]):
            score += 30.0
        elif any(b in branch for b in ["electronics", "electrical", "ece", "eee", "math"]):
            score += 20.0
        else:
            score += 10.0

        # CGPA (30 pts)
        cgpa = profile.cgpa or 7.5
        if cgpa >= 8.5:
            score += 30.0
        elif cgpa >= 7.5:
            score += 25.0
        elif cgpa >= 6.5:
            score += 15.0
        else:
            score += 10.0

        return round(min(100.0, score), 1)

    @classmethod
    def compute_semantic_similarity(
        cls,
        candidate_embedding: List[float],
        job_embedding: Optional[List[float]],
    ) -> Tuple[float, float]:
        """
        Calculate cosine similarity between candidate vector and job vector.
        """
        if not job_embedding or not candidate_embedding:
            return 60.0, 0.60

        raw_cosine = JobEmbeddingService.cosine_similarity(candidate_embedding, job_embedding)
        semantic_score = round(raw_cosine * 100.0, 1)
        return min(100.0, max(0.0, semantic_score)), round(raw_cosine, 3)

    @classmethod
    def compute_evidence_strength(
        cls,
        matched_skills: List[str],
        user_skills: List[UserSkill],
    ) -> Tuple[float, float]:
        """
        Calculate verifiable proof density in the Career Digital Twin for matched skills.
        """
        if not matched_skills:
            return 50.0, 0.0

        skill_map = {us.skill.name.lower(): us for us in user_skills if us.skill}
        evidence_counts = 0
        total_matched = len(matched_skills)

        for ms in matched_skills:
            us = skill_map.get(ms.lower())
            if us and us.evidence and len(us.evidence) > 0:
                evidence_counts += 1

        ratio = evidence_counts / total_matched
        score = 50.0 + (ratio * 50.0)
        return round(min(100.0, score), 1), round(ratio, 3)

    @classmethod
    def compute_preference_fit(
        cls,
        profile: Optional[UserProfile],
        job: Job,
    ) -> float:
        """
        Evaluate workplace mode, employment type, and target salary alignment.
        """
        score = 40.0  # Base alignment

        if profile:
            # Remote / Location Preference (30 pts)
            if profile.remote_preference and job.location_type in ["REMOTE", "HYBRID"]:
                score += 30.0
            elif not profile.remote_preference and job.location_type in ["ONSITE", "HYBRID"]:
                score += 30.0
            else:
                score += 15.0

            # Target roles matching job title (30 pts)
            target_roles = profile.target_roles or []
            job_title_lower = job.title.lower()
            matched_role = any(
                any(w in job_title_lower for w in r.lower().split())
                for r in target_roles
            )
            if matched_role or not target_roles:
                score += 30.0
            else:
                score += 15.0
        else:
            score += 30.0

        return round(min(100.0, score), 1)

    @classmethod
    def generate_explanation(
        cls,
        overall_score: float,
        matched_required: List[str],
        missing_required: List[str],
        matched_preferred: List[str],
        skill_score: float,
        exp_score: float,
        edu_score: float,
        sem_score: float,
        evid_score: float,
        profile: Optional[UserProfile],
        job: Job,
    ) -> MatchExplanation:
        strengths: List[str] = []
        gaps: List[str] = []
        recommendations: List[str] = []

        # Strengths
        if len(matched_required) > 0:
            strengths.append(f"Strong match on {len(matched_required)} core required skill(s): {', '.join(matched_required[:4])}.")
        if sem_score >= 70.0:
            strengths.append(f"High domain-semantic alignment ({sem_score:.0f}%) with {job.company}'s engineering tech stack.")
        if evid_score >= 80.0:
            strengths.append("Robust verifiable project and repository evidence backing your technical skills in your Career Twin.")
        if edu_score >= 90.0:
            strengths.append("Academic degree, branch, and CGPA align closely with target hiring criteria.")

        # Gaps
        if len(missing_required) > 0:
            gaps.append(f"Missing core required skill(s): {', '.join(missing_required)}.")
            for miss in missing_required[:3]:
                recommendations.append(f"Build a project demonstrating {miss} or complete relevant exercises to bridge this gap.")
        if exp_score < 75.0:
            gaps.append(f"Role prefers {job.min_experience_years or 1}+ years experience (current profile: {profile.experience_level if profile else 'entry_level'}).")
            recommendations.append("Highlight production complexity in your project portfolio to compensate for professional years.")
        if evid_score < 65.0 and matched_required:
            recommendations.append("Attach GitHub repository links and deployment URLs to your declared skills in your Profile.")

        if not gaps:
            strengths.append("Exceptional alignment across all required technical criteria!")

        return MatchExplanation(
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
        )

    @classmethod
    def evaluate_match(
        cls,
        profile: Optional[UserProfile],
        user_skills: List[UserSkill],
        candidate_embedding: List[float],
        project_count: int,
        job: Job,
    ) -> Tuple[float, float, float, float, float, float, float, List[str], List[str], List[str], List[str], MatchBreakdown, MatchExplanation]:
        candidate_skill_names = {us.skill.name for us in user_skills if us.skill}

        # 1. Skill Match
        skill_score, matched_req, missing_req, matched_pref, missing_pref, req_ratio, pref_ratio = cls.compute_skill_match(
            candidate_skills=candidate_skill_names,
            job_skills=job.job_skills,
        )

        # 2. Experience Fit
        exp_score = cls.compute_experience_fit(profile, job, project_count)

        # 3. Education Fit
        edu_score = cls.compute_education_fit(profile, job)

        # 4. Semantic Similarity
        sem_score, cosine_raw = cls.compute_semantic_similarity(candidate_embedding, job.embedding)

        # 5. Evidence Strength
        all_matched = matched_req + matched_pref
        evid_score, evid_ratio = cls.compute_evidence_strength(all_matched, user_skills)

        # 6. Preference Fit
        pref_score = cls.compute_preference_fit(profile, job)

        # Overall Weighted Score
        overall = (
            cls.WEIGHT_SKILL * skill_score
            + cls.WEIGHT_EXPERIENCE * exp_score
            + cls.WEIGHT_EDUCATION * edu_score
            + cls.WEIGHT_SEMANTIC * sem_score
            + cls.WEIGHT_EVIDENCE * evid_score
            + cls.WEIGHT_PREFERENCE * pref_score
        )
        overall_score = round(min(100.0, max(0.0, overall)), 1)

        breakdown = MatchBreakdown(
            weights={
                "skill": cls.WEIGHT_SKILL,
                "experience": cls.WEIGHT_EXPERIENCE,
                "education": cls.WEIGHT_EDUCATION,
                "semantic": cls.WEIGHT_SEMANTIC,
                "evidence": cls.WEIGHT_EVIDENCE,
                "preference": cls.WEIGHT_PREFERENCE,
            },
            sub_scores={
                "skill": skill_score,
                "experience": exp_score,
                "education": edu_score,
                "semantic": sem_score,
                "evidence": evid_score,
                "preference": pref_score,
            },
            required_coverage_ratio=req_ratio,
            preferred_coverage_ratio=pref_ratio,
            verified_evidence_ratio=evid_ratio,
            semantic_cosine_raw=cosine_raw,
        )

        explanation = cls.generate_explanation(
            overall_score=overall_score,
            matched_required=matched_req,
            missing_required=missing_req,
            matched_preferred=matched_pref,
            skill_score=skill_score,
            exp_score=exp_score,
            edu_score=edu_score,
            sem_score=sem_score,
            evid_score=evid_score,
            profile=profile,
            job=job,
        )

        return (
            overall_score,
            skill_score,
            exp_score,
            edu_score,
            sem_score,
            evid_score,
            pref_score,
            matched_req,
            missing_req,
            matched_pref,
            missing_pref,
            breakdown,
            explanation,
        )
