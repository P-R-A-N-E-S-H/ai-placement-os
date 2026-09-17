from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.roadmap import (
    LearningRoadmapResponse,
    LearningRoadmapSummary,
    RoadmapGenerateRequest,
    RoadmapTaskResponse,
    TaskToggleRequest,
)
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/learning/roadmaps", tags=["Adaptive Learning Roadmaps"])


@router.post(
    "/generate",
    response_model=LearningRoadmapResponse,
    summary="Generate Adaptive Learning Roadmap",
)
async def generate_roadmap(
    payload: RoadmapGenerateRequest = RoadmapGenerateRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LearningRoadmapResponse:
    """
    Synthesizes a structured multi-week learning curriculum from Phase 6 Skill Gaps,
    creating weekly modules, daily tasks, and curated resources.
    """
    return await RoadmapService.generate_roadmap(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )


@router.get(
    "/active",
    response_model=LearningRoadmapResponse,
    summary="Get Active Learning Roadmap",
)
async def get_active_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LearningRoadmapResponse:
    """
    Retrieves candidate's currently active roadmap with full modules and tasks,
    or auto-generates one if none exists.
    """
    return await RoadmapService.get_active_roadmap(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "",
    response_model=List[LearningRoadmapSummary],
    summary="List Candidate's Roadmaps",
)
async def list_roadmaps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[LearningRoadmapSummary]:
    """Lists all historical and active roadmaps for candidate."""
    return await RoadmapService.list_roadmaps(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{roadmap_id}",
    response_model=LearningRoadmapResponse,
    summary="Get Specific Roadmap by ID",
)
async def get_roadmap_by_id(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LearningRoadmapResponse:
    """Retrieves full roadmap with modules and task checklist."""
    return await RoadmapService.get_roadmap_by_id(
        db=db,
        user_id=current_user.id,
        roadmap_id=roadmap_id,
    )


@router.patch(
    "/tasks/{task_id}/toggle",
    response_model=RoadmapTaskResponse,
    summary="Toggle Task Completion & Sync with Career Twin",
)
async def toggle_task_completion(
    task_id: str,
    payload: TaskToggleRequest = TaskToggleRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RoadmapTaskResponse:
    """
    Toggles task completion state, updates module/roadmap progress,
    and automatically logs verifiable SkillEvidence in the Career Twin.
    """
    return await RoadmapService.toggle_task_completion(
        db=db,
        user_id=current_user.id,
        task_id=task_id,
        payload=payload,
    )
