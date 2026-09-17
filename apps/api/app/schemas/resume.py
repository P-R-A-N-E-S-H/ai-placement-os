from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    graduation_year: Optional[int] = None


class ExperienceItem(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    duration: Optional[str] = None
    bullet_points: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    bullet_points: List[str] = Field(default_factory=list)
    link: Optional[str] = None


class ParsedResumeData(BaseModel):
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    education: List[EducationItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class ATSScorecard(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0)
    sub_scores: Dict[str, float]
    strengths: List[str]
    actionable_improvements: List[str]
    missing_sections: List[str]
    quantification_ratio: float
    canonical_skills_matched_count: int


class ResumeDetailResponse(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_type: str
    file_size_bytes: int
    parsed_data: ParsedResumeData
    ats_score: float
    ats_feedback: ATSScorecard
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeUploadResponse(BaseModel):
    id: str
    file_name: str
    file_type: str
    file_size_bytes: int
    raw_text_length: int
    message: str
