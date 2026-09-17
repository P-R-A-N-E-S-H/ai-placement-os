from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.interview import (
    InterviewCreateRequest,
    InterviewRespondRequest,
    InterviewSessionDetail,
    InterviewSessionSummary,
    InterviewSubmitTurnResult,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["Mock Interview Simulation"])


@router.post(
    "/sessions/create",
    response_model=InterviewSessionDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create & Start Mock Interview Session",
)
async def create_session(
    payload: InterviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewSessionDetail:
    """
    Synthesizes multi-round placement interview questions and initializes active session.
    """
    return await InterviewService.create_session(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )


@router.get(
    "/sessions/active",
    response_model=Optional[InterviewSessionDetail],
    summary="Get Active In-Progress Interview Session",
)
async def get_active_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Optional[InterviewSessionDetail]:
    """
    Retrieves the candidate's current in-progress mock interview session if active.
    """
    return await InterviewService.get_active_session(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=InterviewSessionDetail,
    summary="Get Interview Session Detail & Executive Scorecard",
)
async def get_session_by_id(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewSessionDetail:
    """
    Returns full session details including all questions, candidate responses,
    turn-by-turn rubric critiques, and overall scorecard.
    """
    return await InterviewService.get_session_by_id(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )


@router.get(
    "/sessions",
    response_model=List[InterviewSessionSummary],
    summary="List Candidate Interview Sessions",
)
async def list_sessions(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[InterviewSessionSummary]:
    """
    Lists historical interview sessions for the authenticated candidate.
    """
    return await InterviewService.list_user_sessions(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )


@router.post(
    "/sessions/{session_id}/respond",
    response_model=InterviewSubmitTurnResult,
    summary="Submit Response & Get Instant AI Critique",
)
async def respond_to_question(
    session_id: str,
    payload: InterviewRespondRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewSubmitTurnResult:
    """
    Evaluates candidate's answer for the current question across 4 rubric dimensions,
    provides constructive feedback, and advances the session.
    """
    return await InterviewService.respond_to_question(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
        payload=payload,
    )
