import re
from typing import Any, Dict, List, Set, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill, SkillAlias


class ExtractedJobSkill:
    def __init__(
        self,
        skill_id: str,
        skill_name: str,
        category: str,
        slug: str,
        is_required: bool = True,
        importance_score: float = 1.0,
    ):
        self.skill_id = skill_id
        self.skill_name = skill_name
        self.category = category
        self.slug = slug
        self.is_required = is_required
        self.importance_score = importance_score


class JobSkillExtractor:
    """Extracts canonical skills from job content and classifies into Must-Have vs Nice-to-Have."""

    REQUIRED_PATTERNS = [
        r"(requirements|qualifications|must have|essential|core skills|what you need)",
    ]

    PREFERRED_PATTERNS = [
        r"(nice to have|preferred|bonus|good to have|plus|desired)",
    ]

    @classmethod
    async def extract_skills_for_job(
        cls,
        db: AsyncSession,
        title: str,
        description: str,
        raw_tags: List[str],
    ) -> List[ExtractedJobSkill]:
        # 1. Fetch taxonomy from DB
        skills_res = await db.execute(select(Skill))
        all_skills = {s.id: s for s in skills_res.scalars().all()}

        aliases_res = await db.execute(select(SkillAlias))
        all_aliases = aliases_res.scalars().all()
        alias_map = {a.alias.lower(): a.canonical_skill_id for a in all_aliases}

        combined_text = f"{title}\n{description}\n" + " ".join(raw_tags)
        text_lower = combined_text.lower()
        title_lower = title.lower()

        # Split description into sections if headers present
        preferred_section_text = ""
        preferred_match = re.search(
            r"(?:preferred qualifications|preferred|nice to have|bonus|good to have)[\s\:\-]+(.*?)(?=(?:\n\s*(?:requirements|must have|responsibilities))|$)",
            text_lower,
            re.DOTALL,
        )
        if preferred_match:
            preferred_section_text = preferred_match.group(1)

        matched_skills: Dict[str, ExtractedJobSkill] = {}

        for alias_str, skill_id in alias_map.items():
            pattern = r"\b" + re.escape(alias_str) + r"\b"
            if re.search(pattern, text_lower):
                skill_obj = all_skills.get(skill_id)
                if not skill_obj:
                    continue

                # Check if in title -> High importance
                is_in_title = bool(re.search(pattern, title_lower))
                is_in_preferred = bool(
                    preferred_section_text and re.search(pattern, preferred_section_text)
                )

                is_required = True
                importance = 0.85
                if is_in_title:
                    importance = 1.0
                    is_required = True
                elif is_in_preferred:
                    importance = 0.6
                    is_required = False

                # If already matched via another alias, keep higher importance
                if skill_id in matched_skills:
                    if importance > matched_skills[skill_id].importance_score:
                        matched_skills[skill_id].importance_score = importance
                        matched_skills[skill_id].is_required = is_required
                else:
                    matched_skills[skill_id] = ExtractedJobSkill(
                        skill_id=skill_obj.id,
                        skill_name=skill_obj.name,
                        category=skill_obj.category,
                        slug=skill_obj.slug,
                        is_required=is_required,
                        importance_score=importance,
                    )

        return list(matched_skills.values())
