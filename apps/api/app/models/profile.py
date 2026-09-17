from typing import Any, List, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class UserProfile(Base, UUIDMixin, TimestampMixin):
    """Candidate Career Digital Twin root profile storing academic, aspirational, and portfolio data."""
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    headline: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    college: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    degree: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )
    branch: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )
    graduation_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    cgpa: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    target_roles: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    preferred_locations: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    remote_preference: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    experience_level: Mapped[str] = mapped_column(
        String(64),
        default="entry_level",
        nullable=False,
    )
    career_goal: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    weekly_available_hours: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )
    profile_completion: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    github_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    portfolio_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    user = relationship("User", back_populates="profile")
