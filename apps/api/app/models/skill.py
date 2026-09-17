from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"
    FRAMEWORK = "FRAMEWORK"
    LIBRARY = "LIBRARY"
    DATABASE = "DATABASE"
    CLOUD = "CLOUD"
    DEVOPS = "DEVOPS"
    AI_ML = "AI_ML"
    DATA = "DATA"
    WEB = "WEB"
    MOBILE = "MOBILE"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"
    SOFT_SKILL = "SOFT_SKILL"
    DSA = "DSA"
    OTHER = "OTHER"


class EvidenceSourceType(str, Enum):
    USER_DECLARED = "USER_DECLARED"
    RESUME = "RESUME"
    PROJECT = "PROJECT"
    GITHUB = "GITHUB"
    DSA = "DSA"
    INTERVIEW = "INTERVIEW"
    ASSESSMENT = "ASSESSMENT"
    CERTIFICATION = "CERTIFICATION"
    LEARNING = "LEARNING"


class Skill(Base, UUIDMixin, TimestampMixin):
    """Canonical Skill Taxonomy entity."""
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(64),
        default=SkillCategory.OTHER.value,
        index=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    parent_skill_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Hierarchical and relational mappings
    parent_skill = relationship("Skill", remote_side="Skill.id", backref="child_skills")
    aliases = relationship("SkillAlias", back_populates="canonical_skill", cascade="all, delete-orphan")
    user_skills = relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")
    evidence = relationship("SkillEvidence", back_populates="skill", cascade="all, delete-orphan")


class SkillAlias(Base, UUIDMixin):
    """Deterministic alias mapping to canonical skills (e.g. 'js' -> 'JavaScript')."""
    __tablename__ = "skill_aliases"

    alias: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    canonical_skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    canonical_skill = relationship("Skill", back_populates="aliases")


class UserSkill(Base, UUIDMixin, TimestampMixin):
    """Candidate-skill association with proficiency, confidence, and verification tracking."""
    __tablename__ = "user_skills"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    proficiency: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )
    years_experience: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(64),
        default=EvidenceSourceType.USER_DECLARED.value,
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")
    evidence = relationship(
        "SkillEvidence",
        primaryjoin="and_(UserSkill.user_id==SkillEvidence.user_id, UserSkill.skill_id==SkillEvidence.skill_id)",
        foreign_keys="[SkillEvidence.user_id, SkillEvidence.skill_id]",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
        Index("ix_user_skills_user_prof", "user_id", "proficiency"),
    )


class SkillEvidence(Base, UUIDMixin):
    """Verifiable proof connecting candidates' skills to concrete projects, resumes, or code."""
    __tablename__ = "skill_evidence"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(64),
        default=EvidenceSourceType.USER_DECLARED.value,
        nullable=False,
        index=True,
    )
    source_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    evidence_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )
    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="evidence")
    skill = relationship("Skill", back_populates="evidence")
