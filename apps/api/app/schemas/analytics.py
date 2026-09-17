from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SkillSummaryItem(BaseModel):
    name: str
    proficiency: float
    category: str
    verified: bool


class AnalyticsOverviewResponse(BaseModel):
    placement_readiness_score: float
    skill_match_percentage: float
    total_skills_count: int
    verified_skills_count: int
    dsa_problems_solved: Optional[int] = 0
    mock_interview_score: Optional[float] = None
    profile_completion: float
    active_agents_count: int = 7
    top_skills: List[SkillSummaryItem] = []
    target_roles: List[str] = []
    total_applications: int = 0
    interviewing_applications: int = 0
    offers_received: int = 0
    is_seeded_demo: bool = False


class SubsystemHealth(BaseModel):
    name: str
    status: str
    latency_ms: int
    records_count: int


class ObservabilityHealthResponse(BaseModel):
    status: str
    environment: str
    database_status: str
    total_users: int
    total_jobs: int
    total_resumes: int
    total_dsa_problems: int
    total_dsa_submissions: int
    total_interview_sessions: int
    total_rag_documents: int
    total_workflows: int
    total_applications: int
    subsystems: List[SubsystemHealth]


class VelocityTrajectoryPoint(BaseModel):
    week_label: str
    readiness_score: float
    dsa_count: int
    skills_acquired: int
    mock_score: float


class VelocityTrajectoryResponse(BaseModel):
    target_role: str
    current_readiness: float
    projected_ready_date: str
    trajectory_points: List[VelocityTrajectoryPoint]
