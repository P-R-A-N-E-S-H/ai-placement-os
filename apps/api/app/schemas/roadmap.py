from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskTypeEnum(str, Enum):
    CONCEPT = "CONCEPT"
    PRACTICE = "PRACTICE"
    PROJECT = "PROJECT"
    QUIZ = "QUIZ"


class ModuleStatusEnum(str, Enum):
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class RoadmapStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class TaskResourceItem(BaseModel):
    title: str
    url: str
    type: str = "DOCS"  # 'DOCS', 'VIDEO', 'GITHUB', 'LAB'
    description: Optional[str] = None


class RoadmapTaskResponse(BaseModel):
    id: str
    roadmap_id: str
    module_id: str
    day_number: int
    title: str
    description: str
    task_type: str
    skill_slug: str
    estimated_minutes: int
    resources: List[TaskResourceItem] = Field(default_factory=list)
    is_completed: bool
    completed_at: Optional[datetime] = None
    evidence_text: Optional[str] = None
    evidence_source_id: Optional[str] = None
    order_index: int

    class Config:
        from_attributes = True


class RoadmapModuleResponse(BaseModel):
    id: str
    roadmap_id: str
    week_number: int
    title: str
    description: str
    focus_skills: List[str] = Field(default_factory=list)
    estimated_hours: float
    status: str
    order_index: int
    tasks: List[RoadmapTaskResponse] = Field(default_factory=list)
    completed_task_count: int = 0
    total_task_count: int = 0
    progress_percentage: float = 0.0

    class Config:
        from_attributes = True


class LearningRoadmapResponse(BaseModel):
    id: str
    user_id: str
    gap_report_id: Optional[str] = None
    title: str
    description: str
    target_role: str
    target_job_id: Optional[str] = None
    target_job_title: Optional[str] = None
    target_job_company: Optional[str] = None
    total_weeks: int
    weekly_hours: float
    total_estimated_hours: float
    total_tasks: int
    completed_tasks: int
    progress_percentage: float
    status: str
    modules: List[RoadmapModuleResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningRoadmapSummary(BaseModel):
    id: str
    title: str
    target_role: str
    target_job_title: Optional[str] = None
    total_weeks: int
    weekly_hours: float
    total_tasks: int
    completed_tasks: int
    progress_percentage: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoadmapGenerateRequest(BaseModel):
    target_role: Optional[str] = Field(None, description="Target role slug e.g. 'ai-engineer'")
    target_job_id: Optional[str] = Field(None, description="Optional target job UUID")
    total_weeks: Optional[int] = Field(6, ge=1, le=24, description="Target roadmap duration in weeks")
    weekly_hours: Optional[float] = Field(15.0, ge=1.0, le=60.0, description="Weekly available study hours")


class TaskToggleRequest(BaseModel):
    evidence_text: Optional[str] = Field(None, description="Optional proof of work description or notes")
    evidence_source_id: Optional[str] = Field(None, description="Optional GitHub repo link, commit hash, or project URL")
