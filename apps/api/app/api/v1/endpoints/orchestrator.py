from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.models.user import User
from app.schemas.orchestrator import (
    OrchestratorChatRequest,
    OrchestratorChatResponse,
    WorkflowCreateRequest,
    WorkflowSessionResponse,
    WorkflowStepDto,
)
from app.services.orchestrator_service import OrchestratorService

router = APIRouter()


@router.post("/chat", response_model=OrchestratorChatResponse)
async def orchestrator_chat(
    request: OrchestratorChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> OrchestratorChatResponse:
    """
    Autonomous AI Career Copilot conversational entrypoint:
    Orchestrates Skill Gap, RAG Knowledge, Roadmap, DSA Sandbox, and Interview Simulation agents.
    """
    user_id = current_user.id if current_user else None
    return await OrchestratorService.chat_interaction(
        db=db,
        user_id=user_id,
        request=request,
    )


@router.post("/workflows/create", response_model=WorkflowSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_autonomous_workflow(
    request: WorkflowCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> WorkflowSessionResponse:
    """Trigger an autonomous multi-agent execution pipeline for a high-level placement goal."""
    user_id = current_user.id if current_user else None
    session = await OrchestratorService.execute_workflow(
        db=db,
        user_id=user_id,
        request=request,
    )
    # Fetch with steps
    full_session = await OrchestratorService.get_workflow_session(db, session.id)
    if not full_session:
        raise HTTPException(status_code=500, detail="Failed to load created workflow session")

    step_dtos = [WorkflowStepDto.model_validate(s) for s in full_session.steps]
    return WorkflowSessionResponse(
        id=full_session.id,
        user_id=full_session.user_id,
        goal=full_session.goal,
        status=full_session.status,
        plan_steps=full_session.plan_steps,
        current_step_index=full_session.current_step_index,
        summary_response=full_session.summary_response,
        metadata_info=full_session.metadata_info,
        steps=step_dtos,
        created_at=full_session.created_at,
    )


@router.get("/workflows/{session_id}", response_model=WorkflowSessionResponse)
async def get_workflow_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> WorkflowSessionResponse:
    """Inspect workflow execution details, agent sub-tasks, and latency telemetry."""
    session = await OrchestratorService.get_workflow_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workflow session not found")

    step_dtos = [WorkflowStepDto.model_validate(s) for s in session.steps]
    return WorkflowSessionResponse(
        id=session.id,
        user_id=session.user_id,
        goal=session.goal,
        status=session.status,
        plan_steps=session.plan_steps,
        current_step_index=session.current_step_index,
        summary_response=session.summary_response,
        metadata_info=session.metadata_info,
        steps=step_dtos,
        created_at=session.created_at,
    )


@router.get("/workflows", response_model=List[WorkflowSessionResponse])
async def list_workflows(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> List[WorkflowSessionResponse]:
    """List historical multi-agent autonomous workflow sessions."""
    user_id = current_user.id if current_user else None
    sessions = await OrchestratorService.list_user_workflows(db, user_id=user_id, limit=limit)

    results: List[WorkflowSessionResponse] = []
    for s in sessions:
        full_s = await OrchestratorService.get_workflow_session(db, s.id)
        if full_s:
            step_dtos = [WorkflowStepDto.model_validate(step) for step in full_s.steps]
            results.append(
                WorkflowSessionResponse(
                    id=full_s.id,
                    user_id=full_s.user_id,
                    goal=full_s.goal,
                    status=full_s.status,
                    plan_steps=full_s.plan_steps,
                    current_step_index=full_s.current_step_index,
                    summary_response=full_s.summary_response,
                    metadata_info=full_s.metadata_info,
                    steps=step_dtos,
                    created_at=full_s.created_at,
                )
            )
    return results
