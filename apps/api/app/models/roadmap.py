from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class TaskType(str, Enum):
    CONCEPT = "CONCEPT"
    PRACTICE = "PRACTICE"
    PROJECT = "PROJECT"
    QUIZ = "QUIZ"


class ModuleStatus(str, Enum):
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class RoadmapStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class LearningRoadmap(Base, UUIDMixin, TimestampMixin):
    """
    Candidate's Adaptive Learning Roadmap.
    Persists structured week-by-week curriculum synthesized from Phase 6 Skill Gaps.
    """
    __tablename__ = "learning_roadmaps"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gap_report_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("skill_gap_reports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    target_role: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )
    target_job_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
    )
    target_job_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    target_job_company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    total_weeks: Mapped[int] = mapped_column(
        Integer,
        default=6,
        nullable=False,
    )
    weekly_hours: Mapped[float] = mapped_column(
        Float,
        default=15.0,
        nullable=False,
    )
    total_estimated_hours: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    total_tasks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    completed_tasks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=RoadmapStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", backref="roadmaps")
    gap_report = relationship("SkillGapReport", backref="roadmaps")
    modules = relationship("RoadmapModule", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapModule.week_number")
    tasks = relationship("RoadmapTask", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapTask.order_index")


class RoadmapModule(Base, UUIDMixin, TimestampMixin):
    """
    Weekly learning milestone containing structured daily study items.
    """
    __tablename__ = "roadmap_modules"

    roadmap_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("learning_roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    focus_skills: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    estimated_hours: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=ModuleStatus.LOCKED.value,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    roadmap = relationship("LearningRoadmap", back_populates="modules")
    tasks = relationship("RoadmapTask", back_populates="module", cascade="all, delete-orphan", order_by="RoadmapTask.order_index")


class RoadmapTask(Base, UUIDMixin, TimestampMixin):
    """
    Granular daily task (Concept, Practice, Project deliverable, Quiz).
    """
    __tablename__ = "roadmap_tasks"

    roadmap_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("learning_roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roadmap_modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    task_type: Mapped[str] = mapped_column(
        String(32),
        default=TaskType.CONCEPT.value,
        nullable=False,
    )
    skill_slug: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )
    resources: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    evidence_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    evidence_source_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    roadmap = relationship("LearningRoadmap", back_populates="tasks")
    module = relationship("RoadmapModule", back_populates="tasks")
