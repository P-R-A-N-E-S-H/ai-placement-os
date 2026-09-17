import enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class EmploymentType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    INTERNSHIP = "INTERNSHIP"
    CONTRACT = "CONTRACT"
    FREELANCE = "FREELANCE"


class LocationType(str, enum.Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"


class JobSourceType(str, enum.Enum):
    PUBLIC_FEED = "PUBLIC_FEED"
    DIRECT_API = "DIRECT_API"
    CURATED_PLACEMENT = "CURATED_PLACEMENT"
    MANUAL_WEBHOOK = "MANUAL_WEBHOOK"


class Job(Base, UUIDMixin, TimestampMixin):
    """Normalized structured job opportunity with semantic embeddings and canonical skill links."""

    __tablename__ = "jobs"

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company_logo: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    location: Mapped[str] = mapped_column(String(255), index=True, nullable=False, default="Remote")
    location_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=LocationType.REMOTE.value, index=True
    )
    employment_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=EmploymentType.FULL_TIME.value, index=True
    )

    # Experience & Compensation
    min_experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    max_experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")

    # Content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Source & Ingestion Metadata
    source: Mapped[str] = mapped_column(String(100), index=True, nullable=False, default="curated")
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Multi-factor Deduplication & Embeddings
    fingerprint: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)

    # Relational link to associated canonical skills
    job_skills: Mapped[List["JobSkill"]] = relationship(
        "JobSkill",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class JobSkill(Base, UUIDMixin, TimestampMixin):
    """Association between Job and Canonical Skill with requirement level & importance weight."""

    __tablename__ = "job_skills"

    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    years_experience_required: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="job_skills")
    skill: Mapped["Skill"] = relationship("Skill", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )


class JobSourceLog(Base, UUIDMixin, TimestampMixin):
    """Telemetry log tracking provider ingestion runs, counts, durations, and health."""

    __tablename__ = "job_source_logs"

    source_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # SUCCESS, PARTIAL, FAILED
    jobs_fetched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_duplicated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
