from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.job import (
    JobDetailResponse,
    JobIngestRequest,
    JobIngestResponse,
    JobListResponse,
    JobSourceStatusResponse,
)
from app.services.job_discovery_service import JobDiscoveryService

router = APIRouter(prefix="/jobs", tags=["Job Discovery & Ingestion Agent"])


@router.get(
    "",
    response_model=JobListResponse,
    summary="List & Search Job Opportunities",
)
async def list_jobs(
    search: Optional[str] = Query(None, description="Keywords for title, company, or description"),
    location: Optional[str] = Query(None, description="City, country, or location string"),
    location_type: Optional[str] = Query(None, description="REMOTE, HYBRID, or ONSITE"),
    employment_type: Optional[str] = Query(None, description="FULL_TIME, INTERNSHIP, etc."),
    skill: Optional[str] = Query(None, description="Canonical skill name or slug filter"),
    min_salary: Optional[float] = Query(None, description="Minimum compensation threshold"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    """
    Search and filter live/curated software & AI engineering opportunities
    with faceted canonical skill filtering and pagination.
    """
    return await JobDiscoveryService.list_jobs(
        db=db,
        search=search,
        location=location,
        location_type=location_type,
        employment_type=employment_type,
        skill=skill,
        min_salary=min_salary,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/sources/status",
    response_model=JobSourceStatusResponse,
    summary="Get Ingestion Telemetry & Source Health",
)
async def get_sources_status(
    db: AsyncSession = Depends(get_db),
) -> JobSourceStatusResponse:
    """Retrieve telemetry metrics on active jobs and provider health status."""
    return await JobDiscoveryService.get_sources_status(db)


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Get Single Job Details & Canonical Skills",
)
async def get_job_by_id(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> JobDetailResponse:
    """Retrieve full description, requirements, and mapped canonical skills for a job."""
    return await JobDiscoveryService.get_job_by_id(db, job_id)


@router.post(
    "/ingest",
    response_model=JobIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger On-Demand Job Discovery & Ingestion",
)
async def trigger_job_ingestion(
    payload: Optional[JobIngestRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobIngestResponse:
    """
    Execute job ingestion pipeline across extensible providers,
    extracting canonical skills, deduplicating, and computing dense embeddings.
    """
    req = payload or JobIngestRequest()
    return await JobDiscoveryService.ingest_all(
        db=db,
        source_names=req.source_names,
        limit_per_source=req.limit_per_source or 30,
    )
