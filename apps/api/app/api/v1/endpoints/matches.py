from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.match import (
    BatchMatchResponse,
    JobMatchResponse,
    MatchCalculateRequest,
)
from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["Hybrid Job-Resume Matching Engine"])


@router.post(
    "/calculate/{job_id}",
    response_model=JobMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate & Persist Candidate Match Against Job",
)
async def calculate_job_match(
    job_id: str,
    payload: Optional[MatchCalculateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobMatchResponse:
    """
    Execute 6-Factor Hybrid Matching Engine comparing candidate's Career Digital Twin
    (skills, evidence, academics, experience) against the target job posting.
    """
    return await MatchService.calculate_and_persist_match(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )


@router.post(
    "/batch",
    response_model=BatchMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch Match Candidate Against All Active Opportunities",
)
async def batch_calculate_matches(
    limit: int = Query(50, ge=1, le=200, description="Max jobs to match"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BatchMatchResponse:
    """
    Run Hybrid Matching Engine across all active job postings, rank by score descending,
    and persist results into candidate's match history.
    """
    return await MatchService.batch_calculate_matches(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )


@router.get(
    "",
    response_model=List[JobMatchResponse],
    summary="List Candidate Calculated Matches",
)
async def list_candidate_matches(
    min_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum overall match score filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[JobMatchResponse]:
    """Retrieve all previously computed job match scorecards for the authenticated candidate."""
    return await MatchService.list_matches(
        db=db,
        user_id=current_user.id,
        min_score=min_score,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{job_id}",
    response_model=JobMatchResponse,
    summary="Get Match Scorecard for Specific Job",
)
async def get_match_by_job_id(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobMatchResponse:
    """Retrieve existing match scorecard or compute fresh match if not yet calculated."""
    return await MatchService.calculate_and_persist_match(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )
