from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStatsResponse,
    ApplicationUpdateRequest,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Application Pipeline Tracker"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    request: ApplicationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Track a new job application."""
    app_obj = await ApplicationService.create_application(
        db=db,
        user_id=current_user.id,
        request=request,
    )
    return ApplicationResponse.model_validate(app_obj)


@router.get("", response_model=List[ApplicationResponse])
async def list_applications(
    stage: Optional[str] = Query(None, description="Filter by application stage"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ApplicationResponse]:
    """List tracked applications for the authenticated candidate."""
    apps = await ApplicationService.list_applications(
        db=db,
        user_id=current_user.id,
        stage=stage,
        limit=limit,
    )
    return [ApplicationResponse.model_validate(a) for a in apps]


@router.get("/stats", response_model=ApplicationStatsResponse)
async def get_application_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationStatsResponse:
    """Get application pipeline stage breakdown."""
    return await ApplicationService.get_application_stats(
        db=db,
        user_id=current_user.id,
    )


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    request: ApplicationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Update application stage, notes, or interview rounds."""
    app_obj = await ApplicationService.update_application(
        db=db,
        user_id=current_user.id,
        application_id=application_id,
        request=request,
    )
    return ApplicationResponse.model_validate(app_obj)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a tracked job application."""
    await ApplicationService.delete_application(
        db=db,
        user_id=current_user.id,
        application_id=application_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
