from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ApplicationCreateRequest(BaseModel):
    job_id: Optional[str] = None
    company_name: str = Field(..., min_length=2, max_length=128)
    job_title: str = Field(..., min_length=2, max_length=128)
    location: Optional[str] = None
    salary_offered: Optional[str] = None
    stage: str = Field("APPLIED", description="SAVED, APPLIED, OA_SCHEDULED, TECHNICAL_ROUND, HR_ROUND, OFFER_EXTENDED, REJECTED")
    match_score: Optional[float] = None
    notes: Optional[str] = None
    interview_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    metadata_info: Dict[str, Any] = Field(default_factory=dict)


class ApplicationUpdateRequest(BaseModel):
    stage: Optional[str] = None
    salary_offered: Optional[str] = None
    notes: Optional[str] = None
    interview_schedule: Optional[List[Dict[str, Any]]] = None
    metadata_info: Optional[Dict[str, Any]] = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    company_name: str
    job_title: str
    location: Optional[str] = None
    salary_offered: Optional[str] = None
    stage: str
    applied_at: datetime
    match_score: Optional[float] = None
    notes: Optional[str] = None
    interview_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    metadata_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationStatsResponse(BaseModel):
    total_applications: int
    applied_count: int
    oa_scheduled_count: int
    technical_round_count: int
    hr_round_count: int
    offers_count: int
    rejected_count: int
    stage_breakdown: Dict[str, int]
