import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError
from app.models.job import Job, JobSkill
from app.models.match import JobMatch
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.models.skill import SkillEvidence, UserSkill
from app.schemas.match import (
    BatchMatchResponse,
    JobMatchResponse,
    MatchBreakdown,
    MatchExplanation,
)
from app.services.job_discovery_service import JobDiscoveryService
from app.services.job_embedding_service import JobEmbeddingService
from app.services.matching_engine import MatchingEngine
from app.services.profile_service import ProfileService

logger = logging.getLogger("placement_os.match_service")


class MatchService:
    """Orchestrates candidate digital twin retrieval, job evaluation, persistence, and batch ranking."""

    @classmethod
    async def get_candidate_context(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> Tuple[UserProfile, List[UserSkill], List[float], int]:
        """Load candidate profile, skills with evidence, project count, and generate candidate embedding."""
        # 1. Profile
        profile = await ProfileService.get_or_create_profile(db, user_id)

        # 2. User Skills with Evidence
        skills_res = await db.execute(
            select(UserSkill)
            .options(
                selectinload(UserSkill.skill),
                selectinload(UserSkill.evidence),
            )
            .where(UserSkill.user_id == user_id)
        )
        user_skills = list(skills_res.scalars().all())

        # 3. Latest Resume Projects for Embedding Context
        resume_res = await db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        latest_resume = resume_res.scalar_one_or_none()
        projects_text = ""
        project_count = 2  # default baseline

        if latest_resume and latest_resume.parsed_data:
            projects = latest_resume.parsed_data.get("projects", [])
            project_count = max(project_count, len(projects))
            for p in projects:
                title = p.get("title", "")
                bullets = " ".join(p.get("bullet_points", []))
                projects_text += f" {title} {bullets}"

        # 4. Generate candidate dense embedding
        skill_names = [us.skill.name for us in user_skills if us.skill]
        target_role_str = " ".join(profile.target_roles) if profile and profile.target_roles else "Software Engineer"
        candidate_embedding = JobEmbeddingService.generate_candidate_embedding(
            target_role=target_role_str,
            skills=skill_names,
            projects_text=projects_text,
            bio=profile.bio,
        )

        return profile, user_skills, candidate_embedding, project_count

    @classmethod
    def serialize_job_match(cls, match: JobMatch) -> JobMatchResponse:
        job_summary = (
            JobDiscoveryService.serialize_job_summary(match.job)
            if match.job
            else None
        )

        breakdown_data = match.breakdown if isinstance(match.breakdown, dict) else {}
        explanation_data = match.explanation if isinstance(match.explanation, dict) else {}

        return JobMatchResponse(
            id=match.id,
            user_id=match.user_id,
            job_id=match.job_id,
            overall_score=match.overall_score,
            skill_score=match.skill_score,
            experience_score=match.experience_score,
            education_score=match.education_score,
            semantic_score=match.semantic_score,
            evidence_score=match.evidence_score,
            preference_score=match.preference_score,
            matched_required_skills=match.matched_required_skills or [],
            missing_required_skills=match.missing_required_skills or [],
            matched_preferred_skills=match.matched_preferred_skills or [],
            missing_preferred_skills=match.missing_preferred_skills or [],
            breakdown=MatchBreakdown(**breakdown_data),
            explanation=MatchExplanation(**explanation_data),
            calculated_at=match.calculated_at,
            job=job_summary,
        )

    @classmethod
    async def calculate_and_persist_match(
        cls,
        db: AsyncSession,
        user_id: str,
        job_id: str,
    ) -> JobMatchResponse:
        profile, user_skills, cand_embedding, proj_count = await cls.get_candidate_context(db, user_id)

        # Retrieve target job
        job_res = await db.execute(
            select(Job)
            .options(selectinload(Job.job_skills).selectinload(JobSkill.skill))
            .where(Job.id == job_id)
        )
        job = job_res.scalar_one_or_none()
        if not job:
            raise EntityNotFoundError(f"Job with ID '{job_id}' not found")

        # Evaluate match
        (
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
        ) = MatchingEngine.evaluate_match(
            profile=profile,
            user_skills=user_skills,
            candidate_embedding=cand_embedding,
            project_count=proj_count,
            job=job,
        )

        # Upsert JobMatch in DB
        match_res = await db.execute(
            select(JobMatch).where(
                JobMatch.user_id == user_id,
                JobMatch.job_id == job_id,
            )
        )
        match_obj = match_res.scalar_one_or_none()

        if match_obj:
            match_obj.overall_score = overall_score
            match_obj.skill_score = skill_score
            match_obj.experience_score = exp_score
            match_obj.education_score = edu_score
            match_obj.semantic_score = sem_score
            match_obj.evidence_score = evid_score
            match_obj.preference_score = pref_score
            match_obj.matched_required_skills = matched_req
            match_obj.missing_required_skills = missing_req
            match_obj.matched_preferred_skills = matched_pref
            match_obj.missing_preferred_skills = missing_pref
            match_obj.breakdown = breakdown.model_dump()
            match_obj.explanation = explanation.model_dump()
            match_obj.calculated_at = datetime.now(timezone.utc)
        else:
            match_obj = JobMatch(
                user_id=user_id,
                job_id=job_id,
                overall_score=overall_score,
                skill_score=skill_score,
                experience_score=exp_score,
                education_score=edu_score,
                semantic_score=sem_score,
                evidence_score=evid_score,
                preference_score=pref_score,
                matched_required_skills=matched_req,
                missing_required_skills=missing_req,
                matched_preferred_skills=matched_pref,
                missing_preferred_skills=missing_pref,
                breakdown=breakdown.model_dump(),
                explanation=explanation.model_dump(),
                calculated_at=datetime.now(timezone.utc),
            )
            db.add(match_obj)

        await db.commit()
        await db.refresh(match_obj)
        match_obj.job = job

        return cls.serialize_job_match(match_obj)

    @classmethod
    async def batch_calculate_matches(
        cls,
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
    ) -> BatchMatchResponse:
        profile, user_skills, cand_embedding, proj_count = await cls.get_candidate_context(db, user_id)

        # Get all active jobs
        jobs_res = await db.execute(
            select(Job)
            .options(selectinload(Job.job_skills).selectinload(JobSkill.skill))
            .where(Job.is_active == True)
            .order_by(Job.posted_at.desc())
            .limit(limit)
        )
        active_jobs = list(jobs_res.scalars().all())

        matches_list: List[JobMatch] = []

        for job in active_jobs:
            (
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
            ) = MatchingEngine.evaluate_match(
                profile=profile,
                user_skills=user_skills,
                candidate_embedding=cand_embedding,
                project_count=proj_count,
                job=job,
            )

            match_res = await db.execute(
                select(JobMatch).where(
                    JobMatch.user_id == user_id,
                    JobMatch.job_id == job.id,
                )
            )
            match_obj = match_res.scalar_one_or_none()

            if match_obj:
                match_obj.overall_score = overall_score
                match_obj.skill_score = skill_score
                match_obj.experience_score = exp_score
                match_obj.education_score = edu_score
                match_obj.semantic_score = sem_score
                match_obj.evidence_score = evid_score
                match_obj.preference_score = pref_score
                match_obj.matched_required_skills = matched_req
                match_obj.missing_required_skills = missing_req
                match_obj.matched_preferred_skills = matched_pref
                match_obj.missing_preferred_skills = missing_pref
                match_obj.breakdown = breakdown.model_dump()
                match_obj.explanation = explanation.model_dump()
                match_obj.calculated_at = datetime.now(timezone.utc)
            else:
                match_obj = JobMatch(
                    user_id=user_id,
                    job_id=job.id,
                    overall_score=overall_score,
                    skill_score=skill_score,
                    experience_score=exp_score,
                    education_score=edu_score,
                    semantic_score=sem_score,
                    evidence_score=evid_score,
                    preference_score=pref_score,
                    matched_required_skills=matched_req,
                    missing_required_skills=missing_req,
                    matched_preferred_skills=matched_pref,
                    missing_preferred_skills=missing_pref,
                    breakdown=breakdown.model_dump(),
                    explanation=explanation.model_dump(),
                    calculated_at=datetime.now(timezone.utc),
                )
                db.add(match_obj)

            match_obj.job = job
            matches_list.append(match_obj)

        await db.commit()

        # Sort by overall score descending
        matches_list.sort(key=lambda m: m.overall_score, reverse=True)

        return BatchMatchResponse(
            total_evaluated=len(matches_list),
            matches=[cls.serialize_job_match(m) for m in matches_list],
        )

    @classmethod
    async def list_matches(
        cls,
        db: AsyncSession,
        user_id: str,
        min_score: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[JobMatchResponse]:
        query = (
            select(JobMatch)
            .options(
                selectinload(JobMatch.job)
                .selectinload(Job.job_skills)
                .selectinload(JobSkill.skill)
            )
            .where(JobMatch.user_id == user_id)
        )

        if min_score:
            query = query.where(JobMatch.overall_score >= min_score)

        query = query.order_by(JobMatch.overall_score.desc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        res = await db.execute(query)
        matches = res.scalars().all()
        return [cls.serialize_job_match(m) for m in matches]
