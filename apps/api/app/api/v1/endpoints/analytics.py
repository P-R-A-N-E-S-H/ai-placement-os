from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.core.security import decode_token
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    ObservabilityHealthResponse,
    VelocityTrajectoryResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Placement Readiness Analytics"])
security_scheme = HTTPBearer(auto_error=False)


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get Placement Readiness Overview",
)
async def get_analytics_overview(
    request: Request,
    demo: bool = Query(False, description="Explicitly request seeded demo metrics"),
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsOverviewResponse:
    """
    Return candidate's live placement readiness metrics based on database records.
    If unauthenticated or demo=true, returns demo reference data.
    """
    user_id = None
    if auth_credentials and auth_credentials.credentials:
        try:
            payload = decode_token(auth_credentials.credentials)
            if payload.get("type") == "access":
                user_id = payload.get("sub")
        except Exception:
            user_id = None

    return await AnalyticsService.get_user_overview(
        db=db,
        user_id=user_id,
        demo_mode=demo,
    )


@router.get(
    "/observability",
    response_model=ObservabilityHealthResponse,
    summary="Get System Observability & Subsystem Latency Metrics",
)
async def get_observability_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> ObservabilityHealthResponse:
    """Retrieve platform observability telemetry, database record counts, and agent latencies."""
    return await AnalyticsService.get_observability_health(db)


@router.get(
    "/velocity",
    response_model=VelocityTrajectoryResponse,
    summary="Get Placement Readiness Velocity & Projection Trajectory",
)
async def get_velocity_trajectory(
    target_role: str = Query("AI Engineer", description="Target role for trajectory"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> VelocityTrajectoryResponse:
    """Retrieve historical and projected skill readiness velocity."""
    user_id = current_user.id if current_user else None
    return await AnalyticsService.get_velocity_trajectory(
        db=db,
        user_id=user_id,
        target_role=target_role,
    )
