import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.skill import (
    EvidenceSourceType,
    Skill,
    SkillAlias,
    SkillCategory,
    SkillEvidence,
    UserSkill,
)
from app.schemas.skill import (
    NormalizedSkillItem,
    SkillEvidenceCreate,
    UserSkillCreate,
    UserSkillUpdate,
)


def slugify(text: str) -> str:
    """Generate a clean URL/identifier-safe slug."""
    text = text.lower().strip()
    text = text.replace("c++", "cpp").replace("c#", "csharp").replace(".net", "dotnet")
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


class SkillService:
    """Skill Taxonomy management, deterministic normalization, and user proficiency tracking."""

    @staticmethod
    async def get_or_create_canonical_skill(
        db: AsyncSession,
        name: str,
        category: str = SkillCategory.OTHER.value,
        description: Optional[str] = None,
    ) -> Skill:
        slug = slugify(name)
        result = await db.execute(select(Skill).where(or_(Skill.name.ilike(name), Skill.slug == slug)))
        skill = result.scalar_one_or_none()

        if not skill:
            skill = Skill(
                name=name.strip(),
                slug=slug,
                category=category,
                description=description,
            )
            db.add(skill)
            await db.flush()

            # Automatically add self-alias
            alias = SkillAlias(
                alias=name.strip().lower(),
                canonical_skill_id=skill.id,
            )
            db.add(alias)
            await db.commit()
            await db.refresh(skill)

        return skill

    @staticmethod
    async def normalize_skill(db: AsyncSession, raw_input: str) -> NormalizedSkillItem:
        """
        Deterministic normalization:
        1. Check exact alias match (e.g. 'js', 'ecmascript' -> 'JavaScript')
        2. Check canonical skill slug / name match
        """
        cleaned = raw_input.strip()
        cleaned_lower = cleaned.lower()
        slug = slugify(cleaned)

        # 1. Check alias table
        alias_result = await db.execute(
            select(SkillAlias)
            .options(selectinload(SkillAlias.canonical_skill))
            .where(SkillAlias.alias == cleaned_lower)
        )
        alias_record = alias_result.scalar_one_or_none()
        if alias_record and alias_record.canonical_skill:
            return NormalizedSkillItem(
                raw_input=cleaned,
                canonical_name=alias_record.canonical_skill.name,
                slug=alias_record.canonical_skill.slug,
                category=alias_record.canonical_skill.category,
                matched=True,
                skill_id=alias_record.canonical_skill.id,
            )

        # 2. Check canonical skills table
        skill_result = await db.execute(
            select(Skill).where(or_(Skill.slug == slug, Skill.name.ilike(cleaned)))
        )
        skill = skill_result.scalar_one_or_none()
        if skill:
            return NormalizedSkillItem(
                raw_input=cleaned,
                canonical_name=skill.name,
                slug=skill.slug,
                category=skill.category,
                matched=True,
                skill_id=skill.id,
            )

        return NormalizedSkillItem(
            raw_input=cleaned,
            canonical_name=cleaned,
            slug=slug,
            category=SkillCategory.OTHER.value,
            matched=False,
            skill_id=None,
        )

    @staticmethod
    async def add_or_update_user_skill(
        db: AsyncSession,
        user_id: str,
        payload: UserSkillCreate,
    ) -> UserSkill:
        # Resolve skill_id from name or ID
        skill_id = payload.skill_id
        if not skill_id and payload.skill_name:
            norm = await SkillService.normalize_skill(db, payload.skill_name)
            if norm.skill_id:
                skill_id = norm.skill_id
            else:
                # Create newly declared skill if taxonomy doesn't have it
                new_skill = await SkillService.get_or_create_canonical_skill(db, payload.skill_name)
                skill_id = new_skill.id

        if not skill_id:
            raise ValidationError("Either skill_id or skill_name must be provided")

        # Check existing user skill
        result = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill), selectinload(UserSkill.evidence))
            .where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        )
        user_skill = result.scalar_one_or_none()

        if user_skill:
            user_skill.proficiency = payload.proficiency
            user_skill.confidence = payload.confidence
            user_skill.years_experience = payload.years_experience
            user_skill.source = payload.source
        else:
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill_id,
                proficiency=payload.proficiency,
                confidence=payload.confidence,
                years_experience=payload.years_experience,
                source=payload.source,
            )
            db.add(user_skill)
            await db.flush()

        # Add evidence if provided
        if payload.evidence_text:
            evidence = SkillEvidence(
                user_id=user_id,
                skill_id=skill_id,
                source_type=payload.source,
                evidence_text=payload.evidence_text,
                confidence=payload.confidence,
                verified=False,
            )
            db.add(evidence)

        await db.commit()

        # Reload with relationships
        reloaded = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill), selectinload(UserSkill.evidence))
            .where(UserSkill.id == user_skill.id)
        )
        return reloaded.scalar_one()

    @staticmethod
    async def get_user_skills(db: AsyncSession, user_id: str) -> List[UserSkill]:
        result = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill), selectinload(UserSkill.evidence))
            .where(UserSkill.user_id == user_id)
            .order_by(UserSkill.proficiency.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def remove_user_skill(db: AsyncSession, user_id: str, skill_id: str) -> None:
        result = await db.execute(
            select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        )
        user_skill = result.scalar_one_or_none()
        if not user_skill:
            raise EntityNotFoundError("User skill not found")

        await db.delete(user_skill)
        await db.commit()

    @staticmethod
    async def add_evidence(
        db: AsyncSession,
        user_id: str,
        payload: SkillEvidenceCreate,
    ) -> SkillEvidence:
        evidence = SkillEvidence(
            user_id=user_id,
            skill_id=payload.skill_id,
            source_type=payload.source_type,
            source_id=payload.source_id,
            evidence_text=payload.evidence_text,
            confidence=payload.confidence,
            verified=payload.verified,
        )
        db.add(evidence)

        # Update last_verified_at on user_skill if verified
        if payload.verified:
            user_skill_res = await db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == payload.skill_id)
            )
            user_skill = user_skill_res.scalar_one_or_none()
            if user_skill:
                user_skill.last_verified_at = datetime.now(timezone.utc)
                user_skill.confidence = min(1.0, user_skill.confidence + 0.1)

        await db.commit()
        await db.refresh(evidence)
        return evidence
