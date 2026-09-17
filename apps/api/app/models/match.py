from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class JobMatch(Base, UUIDMixin, TimestampMixin):
    """Persisted multi-factor match scorecard between a Candidate Digital Twin and a Job."""

    __tablename__ = "job_matches"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 6 Deterministic Scores (0.0 to 100.0)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    skill_score: Mapped[float] = mapped_column(Float, nullable=False)
    experience_score: Mapped[float] = mapped_column(Float, nullable=False)
    education_score: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    preference_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Structured Skill Breakdown (Directly feeding Phase 6 Skill Gap Engine)
    matched_required_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_required_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    matched_preferred_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_preferred_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Detailed sub-metrics, weights & explanation
    breakdown: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    explanation: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="matches", lazy="selectin")
    job = relationship("Job", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_match"),
    )
