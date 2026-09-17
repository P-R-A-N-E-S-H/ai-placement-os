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


class InterviewType(str, Enum):
    TECHNICAL = "TECHNICAL"
    BEHAVIORAL = "BEHAVIORAL"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"
    MIXED = "MIXED"


class InterviewDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class InterviewSessionStatus(str, Enum):
    CONFIGURED = "CONFIGURED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class QuestionCategory(str, Enum):
    TECHNICAL_DEEP_DIVE = "TECHNICAL_DEEP_DIVE"
    BEHAVIORAL_STAR = "BEHAVIORAL_STAR"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"
    CS_FUNDAMENTALS = "CS_FUNDAMENTALS"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"


class InterviewSession(Base, UUIDMixin, TimestampMixin):
    """
    Candidate Mock Interview Session.
    Tracks session configuration, real-time question progression, and holistic evaluation metrics.
    """
    __tablename__ = "interview_sessions"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    interview_type: Mapped[str] = mapped_column(
        String(32),
        default=InterviewType.MIXED.value,
        nullable=False,
        index=True,
    )
    target_role: Mapped[str] = mapped_column(
        String(128),
        default="AI Engineer",
        nullable=False,
        index=True,
    )
    target_company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    difficulty: Mapped[str] = mapped_column(
        String(32),
        default=InterviewDifficulty.MEDIUM.value,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=InterviewSessionStatus.IN_PROGRESS.value,
        nullable=False,
        index=True,
    )
    current_question_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_questions: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    # Holistic Scoring (0 - 100)
    overall_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    technical_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    behavioral_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    communication_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    tradeoff_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    summary_feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    strengths: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    improvements: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user = relationship("User", backref="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.question_index")
    responses = relationship("InterviewResponse", back_populates="session", cascade="all, delete-orphan", order_by="InterviewResponse.turn_index")


class InterviewQuestion(Base, UUIDMixin):
    """
    Generated or selected interview question for a session.
    """
    __tablename__ = "interview_questions"

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(64),
        default=QuestionCategory.TECHNICAL_DEEP_DIVE.value,
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    context_or_scenario: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    target_competencies: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    evaluation_criteria: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    suggested_duration_seconds: Mapped[int] = mapped_column(
        Integer,
        default=180,
        nullable=False,
    )

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    responses = relationship("InterviewResponse", back_populates="question", cascade="all, delete-orphan")


class InterviewResponse(Base, UUIDMixin, TimestampMixin):
    """
    Candidate's turn response, rubric scoring, and constructive AI feedback.
    """
    __tablename__ = "interview_responses"

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    turn_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    candidate_response_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    audio_duration_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Turn Scoring (0 - 100)
    score: Mapped[float] = mapped_column(
        Float,
        default=70.0,
        nullable=False,
    )
    technical_depth_score: Mapped[float] = mapped_column(
        Float,
        default=70.0,
        nullable=False,
    )
    structure_star_score: Mapped[float] = mapped_column(
        Float,
        default=70.0,
        nullable=False,
    )
    communication_clarity_score: Mapped[float] = mapped_column(
        Float,
        default=70.0,
        nullable=False,
    )
    tradeoff_score: Mapped[float] = mapped_column(
        Float,
        default=70.0,
        nullable=False,
    )

    # Detailed AI Critique
    strengths: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    improvements: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    star_breakdown: Mapped[Dict[str, str]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    exemplary_answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_feedback_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    session = relationship("InterviewSession", back_populates="responses")
    question = relationship("InterviewQuestion", back_populates="responses")

    __table_args__ = (
        Index("ix_interview_responses_session_turn", "session_id", "turn_index"),
    )
