from __future__ import annotations

from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.application import ApplicationStage, JobApplication
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStatsResponse,
    ApplicationUpdateRequest,
)


class ApplicationService:
    """Enterprise Job Application Pipeline Tracker Service."""

    @classmethod
    async def create_application(
        cls,
        db: AsyncSession,
        user_id: str,
        request: ApplicationCreateRequest,
    ) -> JobApplication:
        """Track a new job application."""
        app_obj = JobApplication(
            user_id=user_id,
            job_id=request.job_id,
            company_name=request.company_name,
            job_title=request.job_title,
            location=request.location,
            salary_offered=request.salary_offered,
            stage=request.stage,
            match_score=request.match_score,
            notes=request.notes,
            interview_schedule=request.interview_schedule,
            metadata_info=request.metadata_info,
        )
        db.add(app_obj)
        await db.commit()
        await db.refresh(app_obj)
        return app_obj

    @classmethod
    async def update_application(
        cls,
        db: AsyncSession,
        user_id: str,
        application_id: str,
        request: ApplicationUpdateRequest,
    ) -> JobApplication:
        """Update stage, notes, or interview dates for an application."""
        stmt = select(JobApplication).where(
            JobApplication.id == application_id,
            JobApplication.user_id == user_id,
        )
        res = await db.execute(stmt)
        app_obj = res.scalar_one_or_none()
        if not app_obj:
            raise EntityNotFoundError(f"Application {application_id} not found")

        if request.stage is not None:
            app_obj.stage = request.stage
        if request.salary_offered is not None:
            app_obj.salary_offered = request.salary_offered
        if request.notes is not None:
            app_obj.notes = request.notes
        if request.interview_schedule is not None:
            app_obj.interview_schedule = request.interview_schedule
        if request.metadata_info is not None:
            app_obj.metadata_info = request.metadata_info

        await db.commit()
        await db.refresh(app_obj)
        return app_obj

    @classmethod
    async def list_applications(
        cls,
        db: AsyncSession,
        user_id: str,
        stage: Optional[str] = None,
        limit: int = 50,
    ) -> List[JobApplication]:
        """List tracked applications for candidate with optional stage filter."""
        stmt = (
            select(JobApplication)
            .where(JobApplication.user_id == user_id)
            .order_by(JobApplication.applied_at.desc())
            .limit(limit)
        )
        if stage:
            stmt = stmt.where(JobApplication.stage == stage)

        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def get_application_stats(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> ApplicationStatsResponse:
        """Calculate application stage conversion metrics."""
        apps = await cls.list_applications(db, user_id=user_id, limit=200)

        breakdown: Dict[str, int] = {
            ApplicationStage.SAVED.value: 0,
            ApplicationStage.APPLIED.value: 0,
            ApplicationStage.OA_SCHEDULED.value: 0,
            ApplicationStage.TECHNICAL_ROUND.value: 0,
            ApplicationStage.HR_ROUND.value: 0,
            ApplicationStage.OFFER_EXTENDED.value: 0,
            ApplicationStage.REJECTED.value: 0,
        }

        for a in apps:
            breakdown[a.stage] = breakdown.get(a.stage, 0) + 1

        return ApplicationStatsResponse(
            total_applications=len(apps),
            applied_count=breakdown.get(ApplicationStage.APPLIED.value, 0),
            oa_scheduled_count=breakdown.get(ApplicationStage.OA_SCHEDULED.value, 0),
            technical_round_count=breakdown.get(ApplicationStage.TECHNICAL_ROUND.value, 0),
            hr_round_count=breakdown.get(ApplicationStage.HR_ROUND.value, 0),
            offers_count=breakdown.get(ApplicationStage.OFFER_EXTENDED.value, 0),
            rejected_count=breakdown.get(ApplicationStage.REJECTED.value, 0),
            stage_breakdown=breakdown,
        )

    @classmethod
    async def delete_application(
        cls,
        db: AsyncSession,
        user_id: str,
        application_id: str,
    ) -> bool:
        """Delete an application entry."""
        stmt = select(JobApplication).where(
            JobApplication.id == application_id,
            JobApplication.user_id == user_id,
        )
        res = await db.execute(stmt)
        app_obj = res.scalar_one_or_none()
        if not app_obj:
            raise EntityNotFoundError(f"Application {application_id} not found")

        await db.delete(app_obj)
        await db.commit()
        return True
