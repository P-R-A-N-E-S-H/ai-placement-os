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
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ProblemDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ProblemCategory(str, Enum):
    ARRAYS_HASHING = "Arrays & Hashing"
    TWO_POINTERS = "Two Pointers"
    SLIDING_WINDOW = "Sliding Window"
    STACK = "Stack"
    BINARY_SEARCH = "Binary Search"
    LINKED_LIST = "Linked List"
    TREES = "Trees"
    HEAP_PRIORITY_QUEUE = "Heap / Priority Queue"
    BACKTRACKING = "Backtracking"
    GRAPHS = "Graphs"
    DYNAMIC_PROGRAMMING = "Dynamic Programming"
    GREEDY = "Greedy"
    BIT_MANIPULATION = "Bit Manipulation"
    SYSTEM_DESIGN = "System Design & Concurrency"


class SubmissionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    PENDING = "PENDING"


class DsaProblem(Base, UUIDMixin, TimestampMixin):
    """
    Canonical DSA Placement Problem.
    Contains problem statement, constraints, starter code templates, and complexity goals.
    """
    __tablename__ = "dsa_problems"

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        String(32),
        default=ProblemDifficulty.MEDIUM.value,
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(64),
        default=ProblemCategory.ARRAYS_HASHING.value,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    constraints: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    hints: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    starter_code: Mapped[Dict[str, str]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    expected_time_complexity: Mapped[str] = mapped_column(
        String(64),
        default="O(N)",
        nullable=False,
    )
    expected_space_complexity: Mapped[str] = mapped_column(
        String(64),
        default="O(1)",
        nullable=False,
    )
    acceptance_rate: Mapped[float] = mapped_column(
        Float,
        default=65.0,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Relationships
    test_cases = relationship("DsaTestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("DsaSubmission", back_populates="problem", cascade="all, delete-orphan")


class DsaTestCase(Base, UUIDMixin):
    """
    Test case specification for a DSA problem.
    Supports visible sample test cases and hidden evaluation test cases.
    """
    __tablename__ = "dsa_test_cases"

    problem_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dsa_problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input_data: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    expected_output: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_hidden: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationship
    problem = relationship("DsaProblem", back_populates="test_cases")


class DsaSubmission(Base, UUIDMixin, TimestampMixin):
    """
    Candidate code submission record.
    Tracks execution metrics, test case pass counts, and feedback.
    """
    __tablename__ = "dsa_submissions"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    problem_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dsa_problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(
        String(32),
        default="python",
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=SubmissionStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    runtime_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    memory_mb: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    passed_test_cases: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_test_cases: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    failed_test_case_input: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    failed_test_case_expected: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    failed_test_case_actual: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    user = relationship("User", backref="dsa_submissions")
    problem = relationship("DsaProblem", back_populates="submissions")

    __table_args__ = (
        Index("ix_dsa_submissions_user_problem", "user_id", "problem_id"),
    )


class UserDsaProgress(Base, UUIDMixin, TimestampMixin):
    """
    Aggregated candidate progress per DSA problem.
    Maintains solved state, best runtime, and total attempts.
    """
    __tablename__ = "user_dsa_progress"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    problem_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dsa_problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_solved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    attempts_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    first_solved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    best_runtime_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    last_submitted_code: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    last_language: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
    )

    # Relationships
    user = relationship("User", backref="dsa_progress_records")
    problem = relationship("DsaProblem", backref="candidate_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uq_user_dsa_problem"),
        Index("ix_user_dsa_progress_solved", "user_id", "is_solved"),
    )
