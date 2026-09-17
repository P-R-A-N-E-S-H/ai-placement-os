from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Check system status, database connectivity, and configuration."""
    db_status = "unhealthy"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "llm_provider": {
            "primary": settings.PRIMARY_LLM_PROVIDER,
            "fallback": settings.FALLBACK_LLM_PROVIDER,
        },
        "version": "0.1.0",
    }


@router.get("/ping", summary="Liveness Ping")
async def ping() -> Dict[str, str]:
    """Simple ping for container orchestrator liveness checks."""
    return {"ping": "pong"}
