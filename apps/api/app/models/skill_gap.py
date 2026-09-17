from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class SkillGapReport(Base, UUIDMixin, TimestampMixin):
    """
    Persisted Skill Gap Analysis Report.
    Stores deterministic comparison of candidate skills against a target role or specific job,
    including prerequisite DAG ordering, time estimation, and ROI priority matrix.
    """
    __tablename__ = "skill_gap_reports"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,  # 'ROLE' or 'JOB'
    )
    target_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,  # Role slug or Job UUID
    )
    target_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    target_company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # High-level metrics
    readiness_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    total_skills_required: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    matched_skills_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    missing_critical_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    proficiency_gap_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_estimated_hours: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    estimated_weeks: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    # Detailed Structured Payloads
    gap_items: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    prerequisite_graph: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    priority_matrix: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    learning_pathway: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Relational link to User
    user = relationship("User", backref="skill_gap_reports")

    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target_skill_gap"),
        Index("ix_gap_user_readiness", "user_id", "readiness_score"),
    )
