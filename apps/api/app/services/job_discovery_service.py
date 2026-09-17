import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError
from app.models.job import Job, JobSkill, JobSourceLog
from app.models.skill import Skill
from app.schemas.job import (
    JobDetailResponse,
    JobIngestResponse,
    JobListResponse,
    JobSkillResponse,
    JobSourceStatus,
    JobSourceStatusResponse,
    JobSummaryResponse,
    SourceRunStats,
)
from app.services.job_deduplicator import JobDeduplicator
from app.services.job_embedding_service import JobEmbeddingService
from app.services.job_skill_extractor import JobSkillExtractor
from app.services.job_sources.base import JobSourceProvider, RawJobData
from app.services.job_sources.curated_provider import CuratedPlacementProvider
from app.services.job_sources.public_feed_provider import ArbeitnowFeedProvider
from app.services.skill_service import slugify

logger = logging.getLogger("placement_os.job_discovery")


class JobDiscoveryService:
    """Orchestrates job provider ingestion, deduplication, skill extraction, embeddings, and querying."""

    PROVIDERS: Dict[str, JobSourceProvider] = {
        "curated_placement": CuratedPlacementProvider(),
        "arbeitnow_feed": ArbeitnowFeedProvider(),
    }

    @classmethod
    def serialize_job_skill(cls, js: JobSkill) -> JobSkillResponse:
        return JobSkillResponse(
            id=js.id,
            skill_id=js.skill_id,
            name=js.skill.name if js.skill else "Unknown",
            slug=js.skill.slug if js.skill else "",
            category=js.skill.category if js.skill else "OTHER",
            is_required=js.is_required,
            importance_score=js.importance_score,
            years_experience_required=js.years_experience_required,
        )

    @classmethod
    def serialize_job_summary(cls, job: Job) -> JobSummaryResponse:
        skills = [cls.serialize_job_skill(js) for js in job.job_skills]
        return JobSummaryResponse(
            id=job.id,
            title=job.title,
            slug=job.slug,
            company=job.company,
            company_logo=job.company_logo,
            location=job.location,
            location_type=job.location_type,
            employment_type=job.employment_type,
            min_experience_years=job.min_experience_years,
            max_experience_years=job.max_experience_years,
            min_salary=job.min_salary,
            max_salary=job.max_salary,
            salary_currency=job.salary_currency,
            source=job.source,
            source_url=job.source_url,
            posted_at=job.posted_at,
            is_active=job.is_active,
            skills=skills,
        )

    @classmethod
    def serialize_job_detail(cls, job: Job) -> JobDetailResponse:
        summary = cls.serialize_job_summary(job)
        return JobDetailResponse(
            **summary.model_dump(),
            description=job.description,
            requirements_raw=job.requirements_raw,
            fingerprint=job.fingerprint,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    @classmethod
    async def ingest_source(
        cls,
        db: AsyncSession,
        provider: JobSourceProvider,
        limit: int = 30,
    ) -> SourceRunStats:
        start_time = time.time()
        fetched_count = 0
        inserted_count = 0
        updated_count = 0
        duplicated_count = 0
        error_msg = None
        status_str = "SUCCESS"

        try:
            raw_jobs = await provider.fetch_jobs(limit=limit)
            fetched_count = len(raw_jobs)

            for raw in raw_jobs:
                fingerprint = JobDeduplicator.compute_fingerprint(
                    company=raw.company,
                    title=raw.title,
                    location=raw.location,
                    description=raw.description,
                )

                existing_job = await JobDeduplicator.find_existing_job(db, raw, fingerprint)

                if existing_job:
                    # Update active state & timestamp
                    existing_job.is_active = True
                    existing_job.posted_at = raw.posted_at
                    if raw.min_salary:
                        existing_job.min_salary = raw.min_salary
                    if raw.max_salary:
                        existing_job.max_salary = raw.max_salary
                    updated_count += 1
                    duplicated_count += 1
                else:
                    # Create new job
                    base_slug = slugify(f"{raw.company}-{raw.title}")
                    unique_slug = f"{base_slug}-{fingerprint[:8]}"

                    # Extract canonical skills
                    extracted_skills = await JobSkillExtractor.extract_skills_for_job(
                        db=db,
                        title=raw.title,
                        description=raw.description,
                        raw_tags=raw.raw_tags,
                    )
                    skill_names = [s.skill_name for s in extracted_skills]

                    # Generate semantic embedding
                    embedding = JobEmbeddingService.generate_job_embedding(
                        title=raw.title,
                        company=raw.company,
                        location=raw.location,
                        skills=skill_names,
                        description=raw.description,
                    )

                    new_job = Job(
                        title=raw.title,
                        slug=unique_slug,
                        company=raw.company,
                        company_logo=raw.company_logo,
                        location=raw.location,
                        location_type=raw.location_type,
                        employment_type=raw.employment_type,
                        min_experience_years=raw.min_experience_years,
                        max_experience_years=raw.max_experience_years,
                        min_salary=raw.min_salary,
                        max_salary=raw.max_salary,
                        salary_currency=raw.salary_currency,
                        description=raw.description,
                        requirements_raw=raw.requirements_raw,
                        source=raw.source_name,
                        source_url=raw.source_url,
                        source_job_id=raw.source_job_id,
                        posted_at=raw.posted_at,
                        is_active=True,
                        fingerprint=fingerprint,
                        embedding=embedding,
                    )
                    db.add(new_job)
                    await db.flush()

                    # Add skill associations
                    for s in extracted_skills:
                        job_skill = JobSkill(
                            job_id=new_job.id,
                            skill_id=s.skill_id,
                            is_required=s.is_required,
                            importance_score=s.importance_score,
                            years_experience_required=raw.min_experience_years,
                        )
                        db.add(job_skill)

                    inserted_count += 1

            await db.commit()

        except Exception as e:
            await db.rollback()
            logger.exception(f"Error during ingestion for source '{provider.name}': {str(e)}")
            status_str = "FAILED"
            error_msg = str(e)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Record telemetry log
        log_entry = JobSourceLog(
            source_name=provider.name,
            status=status_str,
            jobs_fetched=fetched_count,
            jobs_inserted=inserted_count,
            jobs_updated=updated_count,
            jobs_duplicated=duplicated_count,
            error_message=error_msg,
            execution_duration_ms=duration_ms,
        )
        db.add(log_entry)
        await db.commit()

        return SourceRunStats(
            source_name=provider.name,
            status=status_str,
            jobs_fetched=fetched_count,
            jobs_inserted=inserted_count,
            jobs_updated=updated_count,
            jobs_duplicated=duplicated_count,
            duration_ms=duration_ms,
            error_message=error_msg,
        )

    @classmethod
    async def ingest_all(
        cls,
        db: AsyncSession,
        source_names: Optional[List[str]] = None,
        limit_per_source: int = 30,
    ) -> JobIngestResponse:
        total_start = time.time()
        source_stats: List[SourceRunStats] = []

        providers_to_run = (
            [cls.PROVIDERS[s] for s in source_names if s in cls.PROVIDERS]
            if source_names
            else list(cls.PROVIDERS.values())
        )

        for provider in providers_to_run:
            stats = await cls.ingest_source(db, provider, limit=limit_per_source)
            source_stats.append(stats)

        total_duration = round((time.time() - total_start) * 1000, 2)

        return JobIngestResponse(
            total_fetched=sum(s.jobs_fetched for s in source_stats),
            total_inserted=sum(s.jobs_inserted for s in source_stats),
            total_updated=sum(s.jobs_updated for s in source_stats),
            total_duplicated=sum(s.jobs_duplicated for s in source_stats),
            duration_ms=total_duration,
            sources=source_stats,
        )

    @classmethod
    async def list_jobs(
        cls,
        db: AsyncSession,
        search: Optional[str] = None,
        location: Optional[str] = None,
        location_type: Optional[str] = None,
        employment_type: Optional[str] = None,
        skill: Optional[str] = None,
        min_salary: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> JobListResponse:
        # Build query
        query = select(Job).options(
            selectinload(Job.job_skills).selectinload(JobSkill.skill)
        ).where(Job.is_active == True)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Job.title.ilike(search_term),
                    Job.company.ilike(search_term),
                    Job.description.ilike(search_term),
                )
            )

        if location:
            query = query.where(Job.location.ilike(f"%{location}%"))

        if location_type:
            query = query.where(Job.location_type == location_type.upper())

        if employment_type:
            query = query.where(Job.employment_type == employment_type.upper())

        if min_salary:
            query = query.where(Job.max_salary >= min_salary)

        if skill:
            # Join with JobSkill and Skill
            skill_subquery = (
                select(JobSkill.job_id)
                .join(Skill, JobSkill.skill_id == Skill.id)
                .where(
                    or_(
                        Skill.name.ilike(f"%{skill}%"),
                        Skill.slug == slugify(skill),
                    )
                )
            )
            query = query.where(Job.id.in_(skill_subquery))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # Pagination & ordering
        offset = (page - 1) * page_size
        query = query.order_by(Job.posted_at.desc()).offset(offset).limit(page_size)

        result = await db.execute(query)
        jobs = result.scalars().all()

        total_pages = max(1, (total + page_size - 1) // page_size)
        items = [cls.serialize_job_summary(j) for j in jobs]

        return JobListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @classmethod
    async def get_job_by_id(cls, db: AsyncSession, job_id: str) -> JobDetailResponse:
        query = select(Job).options(
            selectinload(Job.job_skills).selectinload(JobSkill.skill)
        ).where(Job.id == job_id)

        result = await db.execute(query)
        job = result.scalar_one_or_none()
        if not job:
            raise EntityNotFoundError(f"Job with ID '{job_id}' not found")

        return cls.serialize_job_detail(job)

    @classmethod
    async def get_sources_status(cls, db: AsyncSession) -> JobSourceStatusResponse:
        # Get active jobs count
        count_res = await db.execute(select(func.count(Job.id)).where(Job.is_active == True))
        active_jobs = count_res.scalar() or 0

        # Get latest log for each source
        source_statuses: List[JobSourceStatus] = []
        for src_name in cls.PROVIDERS.keys():
            log_res = await db.execute(
                select(JobSourceLog)
                .where(JobSourceLog.source_name == src_name)
                .order_by(JobSourceLog.created_at.desc())
                .limit(1)
            )
            log = log_res.scalar_one_or_none()
            if log:
                source_statuses.append(
                    JobSourceStatus(
                        source_name=log.source_name,
                        status=log.status,
                        jobs_fetched=log.jobs_fetched,
                        jobs_inserted=log.jobs_inserted,
                        jobs_updated=log.jobs_updated,
                        jobs_duplicated=log.jobs_duplicated,
                        error_message=log.error_message,
                        last_run=log.created_at,
                        duration_ms=log.execution_duration_ms,
                    )
                )
            else:
                source_statuses.append(
                    JobSourceStatus(
                        source_name=src_name,
                        status="IDLE",
                        jobs_fetched=0,
                        jobs_inserted=0,
                        jobs_updated=0,
                        jobs_duplicated=0,
                        error_message=None,
                        last_run=datetime.now(timezone.utc),
                        duration_ms=0.0,
                    )
                )

        return JobSourceStatusResponse(
            sources=source_statuses,
            total_active_jobs=active_jobs,
        )
