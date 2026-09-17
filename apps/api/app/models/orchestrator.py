from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class WorkflowStatus(str, enum.Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentType(str, enum.Enum):
    SUPERVISOR = "SUPERVISOR"
    RESUME_AGENT = "RESUME_AGENT"
    MATCHING_AGENT = "MATCHING_AGENT"
    SKILL_GAP_AGENT = "SKILL_GAP_AGENT"
    ROADMAP_AGENT = "ROADMAP_AGENT"
    DSA_AGENT = "DSA_AGENT"
    INTERVIEW_AGENT = "INTERVIEW_AGENT"
    RAG_KNOWLEDGE_AGENT = "RAG_KNOWLEDGE_AGENT"


class AgentWorkflowSession(Base, UUIDMixin, TimestampMixin):
    """Execution session for a multi-agent autonomous goal workflow."""
    __tablename__ = "agent_workflow_sessions"

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=WorkflowStatus.PENDING.value, nullable=False, index=True)
    plan_steps: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    current_step_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    steps: Mapped[List[AgentWorkflowStep]] = relationship(
        "AgentWorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="AgentWorkflowStep.step_index",
    )


class AgentWorkflowStep(Base, UUIDMixin, TimestampMixin):
    """Discrete step executed by a specialized agent in the workflow graph."""
    __tablename__ = "agent_workflow_steps"

    workflow_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agent_workflow_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_type: Mapped[str] = mapped_column(String(64), nullable=False)
    action_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=WorkflowStatus.PENDING.value, nullable=False)
    input_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    workflow: Mapped[AgentWorkflowSession] = relationship("AgentWorkflowSession", back_populates="steps")
