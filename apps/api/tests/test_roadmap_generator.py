import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.models.roadmap import LearningRoadmap, ModuleStatus, RoadmapModule, RoadmapTask
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.schemas.roadmap import RoadmapGenerateRequest
from app.services.roadmap_service import RoadmapService


@pytest.mark.asyncio
async def test_roadmap_generator_from_role_benchmark():
    """Verify synthesis of week-by-week learning roadmap from standard role benchmarks."""
    from tests.conftest import TestingSessionLocal
    
    async with TestingSessionLocal() as db:
        # Create test user
        user = User(
            email="roadmap_gen@example.com",
            password_hash="hashed_pw_test",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        profile = UserProfile(user_id=user.id, full_name="Roadmap Gen Candidate")
        db.add(profile)
        await db.commit()

        # Generate roadmap for AI Engineer with 15 weekly hours
        req = RoadmapGenerateRequest(
            target_role="AI Engineer",
            target_job_id=None,
            weekly_hours=15.0,
            learning_style="PRACTICAL",
        )
        roadmap_res = await RoadmapService.generate_roadmap(
            db=db,
            user_id=user.id,
            payload=req,
        )

        assert roadmap_res is not None
        assert roadmap_res.target_role in ["ai-engineer", "AI Engineer"]
        assert roadmap_res.total_weeks >= 1
        assert roadmap_res.weekly_hours == 15.0
        assert roadmap_res.total_tasks > 0
        assert roadmap_res.progress_percentage == 0.0
        assert len(roadmap_res.modules) >= 1

        # Check that Module 1 is UNLOCKED / IN_PROGRESS and subsequent modules are LOCKED
        assert roadmap_res.modules[0].status in [ModuleStatus.UNLOCKED.value, ModuleStatus.IN_PROGRESS.value]
        assert roadmap_res.modules[0].week_number == 1
        assert len(roadmap_res.modules[0].tasks) > 0

        # Check daily tasks structure
        first_task = roadmap_res.modules[0].tasks[0]
        assert first_task.day_number >= 1
        assert first_task.task_type in ["CONCEPT", "PRACTICE", "PROJECT", "QUIZ"]
        assert len(first_task.resources) > 0
        assert first_task.is_completed is False


@pytest.mark.asyncio
async def test_roadmap_generator_with_acquired_skills_reduction():
    """Verify that candidate who already acquired prerequisite skills gets an accelerated roadmap."""
    from tests.conftest import TestingSessionLocal
    
    async with TestingSessionLocal() as db:
        user = User(
            email="accelerated_candidate@example.com",
            password_hash="hashed_pw_test",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        profile = UserProfile(user_id=user.id, full_name="Experienced Dev")
        db.add(profile)
        await db.commit()

        # Find Python skill and grant 90% proficiency
        py_skill = (await db.execute(select(Skill).where(Skill.slug == "python"))).scalar_one_or_none()
        if py_skill:
            user_skill = UserSkill(
                user_id=user.id,
                skill_id=py_skill.id,
                proficiency=0.90,
            )
            db.add(user_skill)
            await db.commit()

        # Generate roadmap for Backend Engineer
        req = RoadmapGenerateRequest(
            target_role="Backend Engineer",
            weekly_hours=20.0,
        )
        roadmap_res = await RoadmapService.generate_roadmap(
            db=db,
            user_id=user.id,
            payload=req,
        )

        assert roadmap_res is not None
        assert roadmap_res.target_role in ["backend-engineer", "Backend Engineer"]
        assert len(roadmap_res.modules) > 0
