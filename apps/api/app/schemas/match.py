from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.job import JobSummaryResponse


class MatchExplanation(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class MatchBreakdown(BaseModel):
    weights: Dict[str, float] = Field(default_factory=dict)
    sub_scores: Dict[str, float] = Field(default_factory=dict)
    required_coverage_ratio: float = 0.0
    preferred_coverage_ratio: float = 0.0
    verified_evidence_ratio: float = 0.0
    semantic_cosine_raw: float = 0.0


class JobMatchResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    semantic_score: float
    evidence_score: float
    preference_score: float
    matched_required_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    matched_preferred_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    breakdown: MatchBreakdown = Field(default_factory=MatchBreakdown)
    explanation: MatchExplanation = Field(default_factory=MatchExplanation)
    calculated_at: datetime
    job: Optional[JobSummaryResponse] = None


class BatchMatchResponse(BaseModel):
    total_evaluated: int
    matches: List[JobMatchResponse]


class MatchCalculateRequest(BaseModel):
    force_recalculate: bool = False
