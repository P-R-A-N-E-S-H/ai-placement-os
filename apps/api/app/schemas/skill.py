from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    slug: str = Field(..., min_length=1, max_length=128)
    category: str
    description: Optional[str] = None
    parent_skill_id: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillAliasCreate(BaseModel):
    alias: str
    canonical_skill_id: str


class SkillAliasResponse(BaseModel):
    id: str
    alias: str
    canonical_skill_id: str

    class Config:
        from_attributes = True


class SkillEvidenceBase(BaseModel):
    skill_id: str
    source_type: str = "USER_DECLARED"
    source_id: Optional[str] = None
    evidence_text: str
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    verified: bool = False


class SkillEvidenceCreate(SkillEvidenceBase):
    pass


class SkillEvidenceResponse(SkillEvidenceBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserSkillCreate(BaseModel):
    skill_id: Optional[str] = None
    skill_name: Optional[str] = None
    proficiency: float = Field(0.5, ge=0.0, le=1.0)
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    years_experience: float = Field(1.0, ge=0.0, le=50.0)
    source: str = "USER_DECLARED"
    evidence_text: Optional[str] = None


class UserSkillUpdate(BaseModel):
    proficiency: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    years_experience: Optional[float] = Field(None, ge=0.0, le=50.0)


class UserSkillResponse(BaseModel):
    id: str
    user_id: str
    skill_id: str
    proficiency: float
    confidence: float
    years_experience: float
    last_verified_at: Optional[datetime] = None
    source: str
    created_at: datetime
    updated_at: datetime
    skill: SkillResponse
    evidence: List[SkillEvidenceResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SkillNormalizationRequest(BaseModel):
    raw_skills: List[str]


class NormalizedSkillItem(BaseModel):
    raw_input: str
    canonical_name: str
    slug: str
    category: str
    matched: bool
    skill_id: Optional[str] = None


class SkillNormalizationResponse(BaseModel):
    normalized: List[NormalizedSkillItem]
