from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GapImportanceEnum(str, Enum):
    CRITICAL_REQUIRED = "CRITICAL_REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    PREFERRED = "PREFERRED"


class GapTypeEnum(str, Enum):
    MISSING = "MISSING"
    PROFICIENCY_DEFICIT = "PROFICIENCY_DEFICIT"
    SATISFIED = "SATISFIED"


class PriorityTierEnum(str, Enum):
    P0_QUICK_WIN = "P0_QUICK_WIN"
    P1_CORE_PREREQUISITE = "P1_CORE_PREREQUISITE"
    P2_MAJOR_MILESTONE = "P2_MAJOR_MILESTONE"
    P3_ELECTIVE = "P3_ELECTIVE"


class UnlockStatusEnum(str, Enum):
    ACQUIRED = "ACQUIRED"
    UNLOCKED = "UNLOCKED"
    LOCKED = "LOCKED"


class SkillGapItem(BaseModel):
    skill_name: str
    slug: str
    category: str
    importance: str = GapImportanceEnum.CRITICAL_REQUIRED.value
    current_proficiency: float = Field(0.0, ge=0.0, le=1.0)
    required_proficiency: float = Field(0.7, ge=0.0, le=1.0)
    gap_type: str = GapTypeEnum.MISSING.value
    priority_tier: str = PriorityTierEnum.P1_CORE_PREREQUISITE.value
    unlock_status: str = UnlockStatusEnum.UNLOCKED.value
    prerequisites: List[str] = Field(default_factory=list)
    missing_prerequisites: List[str] = Field(default_factory=list)
    estimated_hours: float = Field(0.0, ge=0.0)
    roi_score: float = Field(0.0, ge=0.0)
    learning_order_index: int = 0
    recommended_action: str = ""


class PrerequisiteNode(BaseModel):
    id: str
    name: str
    category: str
    current_proficiency: float
    required_proficiency: float
    unlock_status: str
    is_gap: bool


class PrerequisiteEdge(BaseModel):
    source: str
    target: str
    label: Optional[str] = None


class PrerequisiteGraph(BaseModel):
    nodes: List[PrerequisiteNode] = Field(default_factory=list)
    edges: List[PrerequisiteEdge] = Field(default_factory=list)


class PriorityMatrixQuadrant(BaseModel):
    quick_wins: List[SkillGapItem] = Field(default_factory=list)
    major_milestones: List[SkillGapItem] = Field(default_factory=list)
    deep_dives: List[SkillGapItem] = Field(default_factory=list)
    electives: List[SkillGapItem] = Field(default_factory=list)


class LearningPathwayStep(BaseModel):
    order: int
    skill_name: str
    slug: str
    category: str
    estimated_hours: float
    priority_tier: str
    unlock_status: str
    prerequisites: List[str] = Field(default_factory=list)
    recommended_action: str


class SkillGapReportResponse(BaseModel):
    id: str
    user_id: str
    target_type: str
    target_id: str
    target_title: str
    target_company: Optional[str] = None
    readiness_score: float
    total_skills_required: int
    matched_skills_count: int
    missing_critical_count: int
    proficiency_gap_count: int
    total_estimated_hours: float
    estimated_weeks: float
    gap_items: List[SkillGapItem]
    prerequisite_graph: PrerequisiteGraph
    priority_matrix: PriorityMatrixQuadrant
    learning_pathway: List[LearningPathwayStep]
    created_at: datetime

    class Config:
        from_attributes = True


class SkillGapRoleRequest(BaseModel):
    target_role: str = Field(..., min_length=2, max_length=128, description="Target role name or slug")
    weekly_hours: float = Field(15.0, ge=1.0, le=100.0, description="Available weekly learning study hours")


class SkillGapJobRequest(BaseModel):
    weekly_hours: float = Field(15.0, ge=1.0, le=100.0, description="Available weekly learning study hours")


class RoleBenchmarkSummary(BaseModel):
    role_slug: str
    role_name: str
    description: str
    category: str
    required_skills: List[Dict[str, Any]]
    preferred_skills: List[Dict[str, Any]]
    typical_ctc_range: str
