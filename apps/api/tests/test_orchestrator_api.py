import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_orchestrator_api_chat_and_workflows(async_client: AsyncClient):
    """Verify autonomous chat copilot and workflow execution endpoints."""
    # 1. Test Chat Copilot endpoint
    chat_payload = {
        "message": "I want to become a Backend Engineer at Amazon. Analyze my profile and generate next actions.",
        "target_role": "Backend Engineer",
        "target_company": "Amazon",
    }
    chat_res = await async_client.post("/api/v1/orchestrator/chat", json=chat_payload)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert len(chat_data["response_text"]) > 20
    assert len(chat_data["agent_invocations"]) >= 3
    assert len(chat_data["suggested_actions"]) >= 2
    assert chat_data["workflow_session_id"] is not None

    wf_id = chat_data["workflow_session_id"]

    # 2. Retrieve workflow execution details
    get_wf_res = await async_client.get(f"/api/v1/orchestrator/workflows/{wf_id}")
    assert get_wf_res.status_code == 200
    wf_detail = get_wf_res.json()
    assert wf_detail["id"] == wf_id
    assert wf_detail["status"] == "COMPLETED"
    assert len(wf_detail["steps"]) >= 3

    # 3. Create discrete autonomous workflow
    create_payload = {
        "goal": "Prepare for Meta Machine Learning Engineer interview rounds",
        "target_role": "AI Engineer",
        "target_company": "Meta",
    }
    create_res = await async_client.post("/api/v1/orchestrator/workflows/create", json=create_payload)
    assert create_res.status_code == 201
    create_data = create_res.json()
    assert create_data["id"] is not None
    assert create_data["status"] == "COMPLETED"
    assert len(create_data["steps"]) >= 4

    # 4. List historical workflows
    list_res = await async_client.get("/api/v1/orchestrator/workflows")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert len(list_data) >= 2
