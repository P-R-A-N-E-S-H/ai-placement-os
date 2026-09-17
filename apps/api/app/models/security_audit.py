from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class SecurityEventType(str, enum.Enum):
    AUTH_FAILURE = "AUTH_FAILURE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    PROMPT_INJECTION_BLOCKED = "PROMPT_INJECTION_BLOCKED"
    SANDBOX_VIOLATION_BLOCKED = "SANDBOX_VIOLATION_BLOCKED"
    PII_DETECTED = "PII_DETECTED"
    SUSPICIOUS_REQUEST = "SUSPICIOUS_REQUEST"


class SecuritySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityEventLog(Base, UUIDMixin, TimestampMixin):
    """Audit log recording platform security violations, rate limit breaches, and guardrail trips."""
    __tablename__ = "security_event_logs"

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(32), default=SecuritySeverity.MEDIUM.value, nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
