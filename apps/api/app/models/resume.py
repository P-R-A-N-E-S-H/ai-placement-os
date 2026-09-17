from typing import Any, Dict, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Resume(Base, UUIDMixin, TimestampMixin):
    """Resume document entity storing raw text, parsed structured metadata, and ATS scoring."""
    __tablename__ = "resumes"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    parsed_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    ats_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    ats_feedback: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan")


class ResumeSection(Base, UUIDMixin):
    """Segmented resume section (Education, Projects, Skills, Experience)."""
    __tablename__ = "resume_sections"

    resume_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    raw_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    structured_content: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    resume = relationship("Resume", back_populates="sections")
