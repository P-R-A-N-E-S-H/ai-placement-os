from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobSkillResponse(BaseModel):
    id: str
    skill_id: str
    name: str
    slug: str
    category: str
    is_required: bool = True
    importance_score: float = 1.0
    years_experience_required: Optional[float] = None


class JobSummaryResponse(BaseModel):
    id: str
    title: str
    slug: str
    company: str
    company_logo: Optional[str] = None
    location: str
    location_type: str
    employment_type: str
    min_experience_years: Optional[float] = 0.0
    max_experience_years: Optional[float] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: str = "INR"
    source: str
    source_url: str
    posted_at: datetime
    is_active: bool
    skills: List[JobSkillResponse] = Field(default_factory=list)


class JobDetailResponse(JobSummaryResponse):
    description: str
    requirements_raw: Optional[str] = None
    fingerprint: str
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    items: List[JobSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobIngestRequest(BaseModel):
    source_names: Optional[List[str]] = None
    limit_per_source: Optional[int] = 30


class SourceRunStats(BaseModel):
    source_name: str
    status: str
    jobs_fetched: int
    jobs_inserted: int
    jobs_updated: int
    jobs_duplicated: int
    duration_ms: float
    error_message: Optional[str] = None


class JobIngestResponse(BaseModel):
    total_fetched: int
    total_inserted: int
    total_updated: int
    total_duplicated: int
    duration_ms: float
    sources: List[SourceRunStats]


class JobSourceStatus(BaseModel):
    source_name: str
    status: str
    jobs_fetched: int
    jobs_inserted: int
    jobs_updated: int
    jobs_duplicated: int
    error_message: Optional[str] = None
    last_run: datetime
    duration_ms: float


class JobSourceStatusResponse(BaseModel):
    sources: List[JobSourceStatus]
    total_active_jobs: int
