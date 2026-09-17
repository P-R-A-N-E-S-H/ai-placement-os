import abc
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.job import EmploymentType, JobSourceType, LocationType


class RawJobData(BaseModel):
    """Normalized payload emitted by any JobSourceProvider before database upsert."""

    source_name: str
    source_job_id: Optional[str] = None
    source_url: str
    title: str
    company: str
    company_logo: Optional[str] = None
    location: str = "Remote"
    location_type: str = LocationType.REMOTE.value
    employment_type: str = EmploymentType.FULL_TIME.value
    min_experience_years: Optional[float] = 0.0
    max_experience_years: Optional[float] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: str = "INR"
    description: str
    requirements_raw: Optional[str] = None
    raw_tags: List[str] = Field(default_factory=list)
    posted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class JobSourceProvider(abc.ABC):
    """Abstract Base Class for all Job Ingestion Providers."""

    def __init__(self, name: str, source_type: JobSourceType):
        self.name = name
        self.source_type = source_type

    @abc.abstractmethod
    async def fetch_jobs(self, limit: int = 30) -> List[RawJobData]:
        """Fetch and normalize jobs from this source."""
        pass

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Check if provider connection/endpoint is healthy."""
        pass
