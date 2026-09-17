import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dsa import DsaProblem, DsaSubmission, SubmissionStatus, UserDsaProgress
from app.models.profile import UserProfile
from app.models.skill import EvidenceSourceType, SkillEvidence, UserSkill
from app.models.user import User
from app.schemas.dsa import DsaRunRequest, DsaSubmitRequest
from app.services.dsa_service import DsaService


@pytest.mark.asyncio
async def test_dsa_service_seed_and_list_problems():
    """Verify canonical problem seeding and listing with category and difficulty filters."""
    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as db:
        # Seed and list
        problems, total = await DsaService.list_problems(db=db)
        assert total >= 8
        assert any(p.slug == "two-sum" for p in problems)
        assert any(p.slug == "binary-search" for p in problems)
        assert any(p.slug == "coin-change" for p in problems)

        # Filter by Easy
        easy_probs, easy_total = await DsaService.list_problems(db=db, difficulty="EASY")
        assert easy_total > 0
        assert all(p.difficulty == "EASY" for p in easy_probs)


@pytest.mark.asyncio
async def test_dsa_service_run_code_on_sample_test_cases():
    """Verify executing code on sample test cases without persisting submission."""
    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as db:
        valid_code = """class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        m = {}
        for i, n in enumerate(nums):
            if target - n in m:
                return [m[target - n], i]
            m[n] = i
        return []
"""
        run_res = await DsaService.run_code(
            db=db,
            identifier="two-sum",
            payload=DsaRunRequest(language="python", code=valid_code),
        )

        assert run_res.status == SubmissionStatus.ACCEPTED.value
        assert run_res.passed_count > 0
        assert run_res.passed_count == run_res.total_count


@pytest.mark.asyncio
async def test_dsa_service_submit_code_and_career_twin_sync():
    """Verify code submission evaluates all test cases, creates submission, and syncs Career Twin evidence."""
    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as db:
        # Create candidate user
        user = User(
            email="dsa_candidate@example.com",
            password_hash="hashed_pw_test",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        profile = UserProfile(user_id=user.id, full_name="DSA Candidate")
        db.add(profile)
        await db.commit()

        valid_two_sum_code = """class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        m = {}
        for i, n in enumerate(nums):
            if target - n in m:
                return [m[target - n], i]
            m[n] = i
        return []
"""
        sub_res = await DsaService.submit_code(
            db=db,
            user_id=user.id,
            identifier="two-sum",
            payload=DsaSubmitRequest(language="python", code=valid_two_sum_code),
        )

        assert sub_res.status == SubmissionStatus.ACCEPTED.value
        assert sub_res.passed_test_cases == sub_res.total_test_cases
        assert sub_res.ai_feedback is not None
        assert "Estimated Time Complexity" in sub_res.ai_feedback

        # Check UserDsaProgress record
        prog = (
            await db.execute(
                select(UserDsaProgress).where(
                    UserDsaProgress.user_id == user.id,
                    UserDsaProgress.problem_id == sub_res.problem_id,
                )
            )
        ).scalar_one_or_none()

        assert prog is not None
        assert prog.is_solved is True
        assert prog.attempts_count == 1
        assert prog.first_solved_at is not None

        # Check Career Twin SkillEvidence logging
        evidences = (
            await db.execute(
                select(SkillEvidence).where(SkillEvidence.user_id == user.id)
            )
        ).scalars().all()

        assert len(evidences) >= 1
        evidence = evidences[0]
        assert evidence.source_type == EvidenceSourceType.DSA.value
        assert "Two Sum" in evidence.evidence_text

        # Check candidate stats
        stats = await DsaService.get_candidate_dsa_stats(db=db, user_id=user.id)
        assert stats.total_solved == 1
        assert stats.easy_solved == 1
        assert stats.overall_accuracy_percentage == 100.0
