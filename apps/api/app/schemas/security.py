from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GuardrailCheckRequest(BaseModel):
    payload_text: str = Field(..., min_length=1)
    payload_type: str = Field("PROMPT", description="PROMPT, CODE, or TEXT")


class GuardrailCheckResponse(BaseModel):
    is_safe: bool
    violation_reason: Optional[str] = None
    sanitized_output: str


class SecurityEventLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    event_type: str
    severity: str
    ip_address: Optional[str] = None
    endpoint: Optional[str] = None
    details: str
    metadata_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True
