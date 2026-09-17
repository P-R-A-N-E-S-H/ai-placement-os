from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import EntityNotFoundError
from app.models.skill import Skill
from app.schemas.skill import (
    NormalizedSkillItem,
    SkillNormalizationRequest,
    SkillNormalizationResponse,
    SkillResponse,
)
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Canonical Skill Taxonomy"])


@router.get(
    "",
    response_model=List[SkillResponse],
    summary="List Canonical Skills",
)
async def list_skills(
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[SkillResponse]:
    """Retrieve canonical industry skills with optional category filtering."""
    query = select(Skill)
    if category:
        query = query.where(Skill.category == category)
    query = query.offset(offset).limit(limit).order_by(Skill.name.asc())

    result = await db.execute(query)
    skills = result.scalars().all()
    return [SkillResponse.model_validate(s) for s in skills]


@router.get(
    "/search",
    response_model=List[SkillResponse],
    summary="Search Skills by Keyword",
)
async def search_skills(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[SkillResponse]:
    """Search skills by name or keyword with autocomplete support."""
    result = await db.execute(
        select(Skill)
        .where(or_(Skill.name.ilike(f"%{q}%"), Skill.slug.ilike(f"%{q}%")))
        .limit(limit)
        .order_by(Skill.name.asc())
    )
    skills = result.scalars().all()
    return [SkillResponse.model_validate(s) for s in skills]


@router.get(
    "/{skill_id}",
    response_model=SkillResponse,
    summary="Get Skill Details",
)
async def get_skill_by_id(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
) -> SkillResponse:
    """Retrieve canonical skill details by ID."""
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise EntityNotFoundError(f"Skill with ID '{skill_id}' not found")
    return SkillResponse.model_validate(skill)


@router.post(
    "/normalize",
    response_model=SkillNormalizationResponse,
    summary="Batch Normalize Skills Deterministically",
)
async def normalize_skills_batch(
    payload: SkillNormalizationRequest,
    db: AsyncSession = Depends(get_db),
) -> SkillNormalizationResponse:
    """Resolve a list of raw user strings (e.g. 'JS', 'pytorch') to canonical skills."""
    normalized_items: List[NormalizedSkillItem] = []
    for raw in payload.raw_skills:
        item = await SkillService.normalize_skill(db, raw)
        normalized_items.append(item)

    return SkillNormalizationResponse(normalized=normalized_items)
