from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStepDto(BaseModel):
    id: str
    step_index: int
    agent_type: str
    action_name: str
    status: str
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    output_payload: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class WorkflowCreateRequest(BaseModel):
    goal: str = Field(..., min_length=3, description="High-level candidate placement goal")
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowSessionResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    goal: str
    status: str
    plan_steps: List[Dict[str, Any]] = Field(default_factory=list)
    current_step_index: int
    summary_response: Optional[str] = None
    metadata_info: Dict[str, Any] = Field(default_factory=dict)
    steps: List[WorkflowStepDto] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class OrchestratorChatRequest(BaseModel):
    message: str = Field(..., min_length=2)
    conversation_id: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None


class OrchestratorSuggestedAction(BaseModel):
    label: str
    action_type: str
    route: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class OrchestratorChatResponse(BaseModel):
    response_text: str
    workflow_session_id: Optional[str] = None
    agent_invocations: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_actions: List[OrchestratorSuggestedAction] = Field(default_factory=list)
    career_twin_status: Dict[str, Any] = Field(default_factory=dict)
