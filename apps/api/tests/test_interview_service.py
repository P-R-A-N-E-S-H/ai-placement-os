import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import InterviewSession, InterviewSessionStatus
from app.models.profile import UserProfile
from app.models.skill import EvidenceSourceType, SkillEvidence, UserSkill
from app.models.user import User
from app.schemas.interview import InterviewCreateRequest, InterviewRespondRequest
from app.services.interview_service import InterviewService


@pytest.mark.asyncio
async def test_interview_session_creation_and_turn_progression():
    """Verify creating a mock interview session, submitting turn responses, and auto-completing with Career Twin sync."""
    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as db:
        user = User(
            email="mock_candidate@example.com",
            password_hash="hashed_pw_test",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        profile = UserProfile(user_id=user.id, full_name="Interview Candidate")
        db.add(profile)
        await db.commit()

        # 1. Create 2-question interview session
        create_req = InterviewCreateRequest(
            interview_type="TECHNICAL",
            target_role="AI Engineer",
            difficulty="MEDIUM",
            total_questions=2,
        )
        session_detail = await InterviewService.create_session(
            db=db,
            user_id=user.id,
            payload=create_req,
        )

        assert session_detail.id is not None
        assert session_detail.total_questions == 2
        assert len(session_detail.questions) == 2
        assert session_detail.status == InterviewSessionStatus.IN_PROGRESS.value

        # 2. Answer Question 1
        ans1 = (
            "Situation: In building our enterprise RAG search, we needed hybrid retrieval. "
            "Task: I led the design of our semantic vector search with pgvector and BM25. "
            "Action: I used LangChain and implemented cross-encoder re-ranking with strict citations. "
            "Result: We improved precision by 35% and reduced p95 latency to 110ms."
        )
        turn1_res = await InterviewService.respond_to_question(
            db=db,
            user_id=user.id,
            session_id=session_detail.id,
            payload=InterviewRespondRequest(candidate_response_text=ans1),
        )

        assert turn1_res.turn_response.score >= 75.0
        assert turn1_res.is_session_completed is False
        assert turn1_res.next_question is not None

        # 3. Answer Question 2 (Final question)
        ans2 = (
            "Situation: Our asynchronous background workers were running out of GPU memory. "
            "Task: Diagnose the memory leak and optimize throughput. "
            "Action: Profiled memory using PyTorch profiler, implemented gradient checkpointing and batch queueing in Celery. "
            "Result: Cut VRAM usage by 50% and supported 4x larger batch sizes with 0 OOM errors."
        )
        turn2_res = await InterviewService.respond_to_question(
            db=db,
            user_id=user.id,
            session_id=session_detail.id,
            payload=InterviewRespondRequest(candidate_response_text=ans2),
        )

        assert turn2_res.is_session_completed is True
        assert turn2_res.next_question is None

        # 4. Check completed session state
        completed_session = await InterviewService.get_session_by_id(
            db=db,
            user_id=user.id,
            session_id=session_detail.id,
        )

        assert completed_session.status == InterviewSessionStatus.COMPLETED.value
        assert completed_session.overall_score is not None
        assert completed_session.overall_score >= 70.0
        assert len(completed_session.responses) == 2
        assert completed_session.summary_feedback is not None

        # 5. Verify Career Twin SkillEvidence logging
        evidences = (
            await db.execute(
                select(SkillEvidence).where(SkillEvidence.user_id == user.id)
            )
        ).scalars().all()

        assert len(evidences) >= 1
        ev = evidences[0]
        assert ev.source_type == EvidenceSourceType.INTERVIEW.value
        assert "AI Engineer" in ev.evidence_text
