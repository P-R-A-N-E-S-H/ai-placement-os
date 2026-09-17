from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.schemas.security import (
    GuardrailCheckRequest,
    GuardrailCheckResponse,
    SecurityEventLogResponse,
)
from app.services.security_service import SecurityService

router = APIRouter(prefix="/security", tags=["Security Hardening & Guardrails"])


@router.post("/guardrail-check", response_model=GuardrailCheckResponse)
async def check_guardrail_payload(
    request: GuardrailCheckRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> GuardrailCheckResponse:
    """Evaluate payload text for AST code safety, adversarial prompt injection, and PII exposure."""
    return SecurityService.evaluate_guardrail(request)


@router.get("/audit-logs", response_model=List[SecurityEventLogResponse])
async def list_security_audit_logs(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> List[SecurityEventLogResponse]:
    """List recent platform security violation audit events."""
    logs = await SecurityService.list_security_logs(db, limit=limit)
    return [SecurityEventLogResponse.model_validate(log) for log in logs]
