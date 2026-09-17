from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.guardrails import GuardrailValidator
from app.models.security_audit import SecurityEventLog, SecurityEventType, SecuritySeverity
from app.schemas.security import GuardrailCheckRequest, GuardrailCheckResponse


class SecurityService:
    """Security event auditing and guardrail evaluation service."""

    @classmethod
    async def log_security_event(
        cls,
        db: AsyncSession,
        event_type: str,
        severity: str,
        details: str,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> SecurityEventLog:
        """Record a security audit log in the database."""
        event = SecurityEventLog(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            endpoint=endpoint,
            details=details,
            metadata_info=metadata_info or {},
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @classmethod
    async def list_security_logs(
        cls,
        db: AsyncSession,
        limit: int = 50,
    ) -> List[SecurityEventLog]:
        """Fetch recent security audit event logs."""
        stmt = select(SecurityEventLog).order_by(SecurityEventLog.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    def evaluate_guardrail(cls, request: GuardrailCheckRequest) -> GuardrailCheckResponse:
        """Run on-demand security and guardrail inspection on input payload."""
        p_type = request.payload_type.upper()
        p_text = request.payload_text

        if p_type == "CODE":
            is_safe, reason = GuardrailValidator.validate_code_sandbox_security(p_text)
            sanitized = GuardrailValidator.sanitize_pii(p_text)
            return GuardrailCheckResponse(
                is_safe=is_safe,
                violation_reason=reason,
                sanitized_output=sanitized,
            )
        elif p_type == "PROMPT":
            is_safe, reason = GuardrailValidator.validate_prompt_injection(p_text)
            sanitized = GuardrailValidator.sanitize_pii(p_text)
            return GuardrailCheckResponse(
                is_safe=is_safe,
                violation_reason=reason,
                sanitized_output=sanitized,
            )
        else:
            sanitized = GuardrailValidator.sanitize_pii(p_text)
            return GuardrailCheckResponse(
                is_safe=True,
                violation_reason=None,
                sanitized_output=sanitized,
            )
