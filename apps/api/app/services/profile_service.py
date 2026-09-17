from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.audit import AuditLog
from app.models.profile import UserProfile
from app.models.skill import SkillEvidence, UserSkill
from app.schemas.profile import ProfileCompletionBreakdown, UserProfileUpdate


class ProfileService:
    """Career Digital Twin Profile management and dynamic completion calculation."""

    @staticmethod
    async def get_or_create_profile(db: AsyncSession, user_id: str, full_name: str = "Candidate") -> UserProfile:
        result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profile = result.scalar_one_or_none()

        if not profile:
            profile = UserProfile(
                user_id=user_id,
                full_name=full_name,
                profile_completion=15.0,
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        return profile

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: str,
        payload: UserProfileUpdate,
        request_id: Optional[str] = None,
    ) -> UserProfile:
        profile = await ProfileService.get_or_create_profile(db, user_id)

        update_dict = payload.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)

        # Recalculate profile completion dynamically
        completion_breakdown = await ProfileService.calculate_completion(db, profile)
        profile.profile_completion = completion_breakdown.overall_completion

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="PROFILE_UPDATED",
            request_id=request_id,
            metadata_json={"updated_fields": list(update_dict.keys())},
        )
        db.add(audit)
        await db.commit()
        await db.refresh(profile)
        return profile

    @staticmethod
    async def calculate_completion(
        db: AsyncSession,
        profile: UserProfile,
    ) -> ProfileCompletionBreakdown:
        """
        Dynamically calculate completion score and missing fields across 7 weighted dimensions:
        - Basic Profile: 15%
        - Education: 15%
        - Skills: 20%
        - Career Goals: 15%
        - Preferences: 10%
        - Evidence/Projects: 15%
        - External Links: 10%
        """
        components: Dict[str, float] = {}
        missing: List[str] = []

        # 1. Basic Info (15%)
        basic_score = 0.0
        if profile.full_name:
            basic_score += 0.08
        if profile.headline or profile.bio:
            basic_score += 0.07
        else:
            missing.append("headline or bio")
        components["basic_profile"] = round(basic_score * 100, 1)

        # 2. Education (15%)
        edu_score = 0.0
        if profile.college:
            edu_score += 0.04
        else:
            missing.append("college")
        if profile.degree and profile.branch:
            edu_score += 0.04
        else:
            missing.append("degree and branch")
        if profile.graduation_year:
            edu_score += 0.04
        else:
            missing.append("graduation_year")
        if profile.cgpa is not None:
            edu_score += 0.03
        else:
            missing.append("cgpa")
        components["education"] = round(edu_score * 100, 1)

        # 3. Skills (20%) - count skills in DB
        skills_count_res = await db.execute(
            select(func.count(UserSkill.id)).where(UserSkill.user_id == profile.user_id)
        )
        skills_count = skills_count_res.scalar() or 0
        if skills_count >= 5:
            skills_score = 0.20
        elif skills_count >= 3:
            skills_score = 0.15
        elif skills_count >= 1:
            skills_score = 0.10
        else:
            skills_score = 0.0
            missing.append("at least 3 skills")
        components["skills"] = round(skills_score * 100, 1)

        # 4. Career Goals & Target Roles (15%)
        goal_score = 0.0
        if profile.target_roles and len(profile.target_roles) > 0:
            goal_score += 0.08
        else:
            missing.append("target_roles")
        if profile.career_goal:
            goal_score += 0.07
        else:
            missing.append("career_goal")
        components["career_goals"] = round(goal_score * 100, 1)

        # 5. Preferences (10%)
        pref_score = 0.0
        if profile.preferred_locations and len(profile.preferred_locations) > 0:
            pref_score += 0.05
        else:
            missing.append("preferred_locations")
        if profile.weekly_available_hours > 0:
            pref_score += 0.05
        components["preferences"] = round(pref_score * 100, 1)

        # 6. Skill Evidence / Projects (15%)
        evidence_count_res = await db.execute(
            select(func.count(SkillEvidence.id)).where(SkillEvidence.user_id == profile.user_id)
        )
        evidence_count = evidence_count_res.scalar() or 0
        if evidence_count >= 3:
            evidence_score = 0.15
        elif evidence_count >= 1:
            evidence_score = 0.10
        else:
            evidence_score = 0.0
            missing.append("skill_evidence")
        components["evidence_and_projects"] = round(evidence_score * 100, 1)

        # 7. External Links (10%)
        links_score = 0.0
        if profile.github_url:
            links_score += 0.05
        else:
            missing.append("github_url")
        if profile.linkedin_url or profile.portfolio_url:
            links_score += 0.05
        else:
            missing.append("linkedin_url")
        components["external_links"] = round(links_score * 100, 1)

        overall = round(
            (basic_score + edu_score + skills_score + goal_score + pref_score + evidence_score + links_score)
            * 100,
            1,
        )

        return ProfileCompletionBreakdown(
            overall_completion=min(100.0, overall),
            components=components,
            missing_fields=missing,
        )
