from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.models.user import User
from app.schemas.dsa import (
    DsaProblemDetail,
    DsaProblemSummary,
    DsaRunRequest,
    DsaRunResponse,
    DsaStatsResponse,
    DsaSubmissionResponse,
    DsaSubmitRequest,
)
from app.services.dsa_service import DsaService

router = APIRouter(prefix="/dsa", tags=["DSA Preparation & Sandbox"])


@router.get(
    "/problems",
    response_model=List[DsaProblemSummary],
    summary="List Canonical DSA Problems",
)
async def list_problems(
    category: Optional[str] = Query(None, description="Filter by topic category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: EASY, MEDIUM, HARD"),
    search: Optional[str] = Query(None, description="Search term in title or category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DsaProblemSummary]:
    """
    Returns curated placement DSA problem catalog with candidate-specific solved flags.
    """
    user_id = current_user.id if current_user else None
    problems, _ = await DsaService.list_problems(
        db=db,
        user_id=user_id,
        category=category,
        difficulty=difficulty,
        search=search,
        page=page,
        page_size=page_size,
    )
    return problems


@router.get(
    "/problems/{identifier}",
    response_model=DsaProblemDetail,
    summary="Get Problem Statement & Sample Test Cases",
)
async def get_problem(
    identifier: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> DsaProblemDetail:
    """
    Retrieves complete problem description, starter templates, and visible sample test cases.
    """
    user_id = current_user.id if current_user else None
    return await DsaService.get_problem_by_slug_or_id(
        db=db,
        identifier=identifier,
        user_id=user_id,
    )


@router.post(
    "/problems/{identifier}/run",
    response_model=DsaRunResponse,
    summary="Run Code on Sample Test Cases",
)
async def run_code(
    identifier: str,
    payload: DsaRunRequest,
    db: AsyncSession = Depends(get_db),
) -> DsaRunResponse:
    """
    Executes candidate code in sandbox against sample test cases or custom input.
    """
    return await DsaService.run_code(
        db=db,
        identifier=identifier,
        payload=payload,
    )


@router.post(
    "/problems/{identifier}/submit",
    response_model=DsaSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Code for Full Evaluation & Career Twin Sync",
)
async def submit_code(
    identifier: str,
    payload: DsaSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DsaSubmissionResponse:
    """
    Evaluates candidate solution across all hidden test cases, persists submission metrics,
    and automatically logs verified SkillEvidence in the Career Twin upon acceptance.
    """
    return await DsaService.submit_code(
        db=db,
        user_id=current_user.id,
        identifier=identifier,
        payload=payload,
    )


@router.get(
    "/submissions",
    response_model=List[DsaSubmissionResponse],
    summary="List Candidate Submissions",
)
async def list_submissions(
    problem_id: Optional[str] = Query(None, description="Optional problem ID filter"),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DsaSubmissionResponse]:
    """
    Lists historical submissions and evaluation results for the authenticated candidate.
    """
    return await DsaService.list_user_submissions(
        db=db,
        user_id=current_user.id,
        problem_id=problem_id,
        limit=limit,
    )


@router.get(
    "/stats",
    response_model=DsaStatsResponse,
    summary="Get Candidate DSA Analytics",
)
async def get_dsa_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DsaStatsResponse:
    """
    Returns candidate's solved problem distribution, accuracy rate, and topic mastery.
    """
    return await DsaService.get_candidate_dsa_stats(
        db=db,
        user_id=current_user.id,
    )
