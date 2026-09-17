from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ApplicationStage(str, enum.Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    OA_SCHEDULED = "OA_SCHEDULED"
    TECHNICAL_ROUND = "TECHNICAL_ROUND"
    HR_ROUND = "HR_ROUND"
    OFFER_EXTENDED = "OFFER_EXTENDED"
    REJECTED = "REJECTED"


class JobApplication(Base, UUIDMixin, TimestampMixin):
    """Tracks candidate job applications and interview lifecycle stages."""
    __tablename__ = "job_applications"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    salary_offered: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    stage: Mapped[str] = mapped_column(
        String(32),
        default=ApplicationStage.APPLIED.value,
        nullable=False,
        index=True,
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interview_schedule: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    metadata_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
