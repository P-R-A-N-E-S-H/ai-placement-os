import pytest
from app.models.orchestrator import WorkflowStatus
from app.schemas.orchestrator import WorkflowCreateRequest
from app.services.orchestrator_service import OrchestratorService
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_orchestrator_service_plan_and_execution():
    """Verify master multi-agent supervisor plan decomposition and execution."""
    async with TestingSessionLocal() as db:
        request = WorkflowCreateRequest(
            goal="I want to crack Google L5 AI Engineer in 60 days. Diagnose my gaps, roadmap, DSA, and interview prep.",
            target_role="AI Engineer",
            target_company="Google",
        )

        session = await OrchestratorService.execute_workflow(
            db=db,
            user_id=None,
            request=request,
        )

        assert session.id is not None
        assert session.status == WorkflowStatus.COMPLETED.value
        assert len(session.plan_steps) >= 4
        assert session.summary_response is not None
        assert "Google" in session.goal
        assert "Readiness" in session.summary_response or "AI Engineer" in session.summary_response

        # Verify steps retrieved from DB
        full_session = await OrchestratorService.get_workflow_session(db, session.id)
        assert full_session is not None
        assert len(full_session.steps) >= 4
        failed_steps = [(s.agent_type, s.status, s.error_message) for s in full_session.steps if s.status != WorkflowStatus.COMPLETED.value]
        assert not failed_steps, f"Steps failed: {failed_steps}"
        assert any(s.agent_type == "SKILL_GAP_AGENT" for s in full_session.steps)
        assert any(s.agent_type == "RAG_KNOWLEDGE_AGENT" for s in full_session.steps)
