import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.models.roadmap import LearningRoadmap, ModuleStatus, RoadmapModule, RoadmapTask
from app.models.skill import EvidenceSourceType, SkillEvidence, UserSkill
from app.models.user import User
from app.schemas.roadmap import RoadmapGenerateRequest, TaskToggleRequest
from app.services.roadmap_service import RoadmapService


@pytest.mark.asyncio
async def test_task_toggle_and_career_twin_evidence_sync():
    """Verify that completing a task records SkillEvidence in Career Twin and updates progress."""
    from tests.conftest import TestingSessionLocal
    
    async with TestingSessionLocal() as db:
        user = User(
            email="evidence_sync_user@example.com",
            password_hash="hashed_pw_test",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        profile = UserProfile(user_id=user.id, full_name="Evidence Candidate")
        db.add(profile)
        await db.commit()

        # Generate AI Engineer roadmap
        req = RoadmapGenerateRequest(
            target_role="AI Engineer",
            weekly_hours=15.0,
        )
        roadmap_res = await RoadmapService.generate_roadmap(
            db=db,
            user_id=user.id,
            payload=req,
        )

        first_task_id = roadmap_res.modules[0].tasks[0].id
        task_skill = roadmap_res.modules[0].tasks[0].skill_slug

        # Toggle task completion with proof of work
        toggle_req = TaskToggleRequest(
            is_completed=True,
            evidence_text="Built LangChain conversational agent with memory buffer and custom tools.",
            evidence_source_id="github.com/candidate/langchain-rag-agent",
        )
        updated_task = await RoadmapService.toggle_task_completion(
            db=db,
            user_id=user.id,
            task_id=first_task_id,
            payload=toggle_req,
        )

        assert updated_task.is_completed is True
        assert updated_task.evidence_text is not None

        # Retrieve active roadmap and check progress
        active_roadmap = await RoadmapService.get_active_roadmap(db=db, user_id=user.id)
        assert active_roadmap is not None
        assert active_roadmap.completed_tasks == 1
        assert active_roadmap.progress_percentage > 0.0

        # Query Career Twin SkillEvidence table
        evidences = (
            await db.execute(
                select(SkillEvidence).where(SkillEvidence.user_id == user.id)
            )
        ).scalars().all()

        assert len(evidences) >= 1
        evidence = evidences[0]
        assert evidence.source_type == EvidenceSourceType.LEARNING.value
        assert "LangChain" in evidence.evidence_text or "Completed" in evidence.evidence_text

        # Query UserSkill table for proficiency gain
        user_skills = (
            await db.execute(
                select(UserSkill).where(UserSkill.user_id == user.id)
            )
        ).scalars().all()
        assert len(user_skills) >= 1
        assert any(us.proficiency > 0.0 for us in user_skills)


@pytest.mark.asyncio
async def test_module_auto_unlock_when_all_tasks_completed():
    """Verify that completing all tasks in Week 1 unlocks Week 2."""
    from tests.conftest import TestingSessionLocal
    
    async with TestingSessionLocal() as db:
        user = User(
            email="unlock_user@example.com",
            password_hash="hashed_pw_test",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        profile = UserProfile(user_id=user.id, full_name="Unlock Candidate")
        db.add(profile)
        await db.commit()

        req = RoadmapGenerateRequest(
            target_role="AI Engineer",
            weekly_hours=20.0,
        )
        roadmap_res = await RoadmapService.generate_roadmap(
            db=db,
            user_id=user.id,
            payload=req,
        )

        if len(roadmap_res.modules) > 1:
            # Complete all tasks in Module 1
            mod1_tasks = roadmap_res.modules[0].tasks
            for task in mod1_tasks:
                await RoadmapService.toggle_task_completion(
                    db=db,
                    user_id=user.id,
                    task_id=task.id,
                    payload=TaskToggleRequest(is_completed=True),
                )

            # Retrieve active roadmap and check module status
            active = await RoadmapService.get_active_roadmap(db=db, user_id=user.id)
            assert active is not None
            assert active.modules[0].status == ModuleStatus.COMPLETED.value
            assert active.modules[1].status in [ModuleStatus.UNLOCKED.value, ModuleStatus.IN_PROGRESS.value]
