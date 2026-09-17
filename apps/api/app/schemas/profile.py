from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class UserProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    headline: Optional[str] = None
    bio: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=2000, le=2040)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    target_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_preference: bool = True
    experience_level: str = "entry_level"
    career_goal: Optional[str] = None
    weekly_available_hours: int = Field(10, ge=1, le=80)
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    headline: Optional[str] = None
    bio: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=2000, le=2040)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    target_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    remote_preference: Optional[bool] = None
    experience_level: Optional[str] = None
    career_goal: Optional[str] = None
    weekly_available_hours: Optional[int] = Field(None, ge=1, le=80)
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class UserProfileResponse(UserProfileBase):
    id: str
    user_id: str
    profile_completion: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileCompletionBreakdown(BaseModel):
    overall_completion: float
    components: Dict[str, float]
    missing_fields: List[str]
