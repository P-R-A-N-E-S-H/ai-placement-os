import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_skill_evidence_logging(async_client: AsyncClient):
    """Test attaching verifiable evidence to candidate skills."""
    reg_payload = {
        "email": "evidenceuser@placementos.ai",
        "password": "Password123!",
        "full_name": "Evidence User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add skill: PyTorch
    add_payload = {
        "skill_name": "PyTorch",
        "proficiency": 0.8,
        "confidence": 0.7,
        "source": "PROJECT",
    }
    add_res = await async_client.post("/api/v1/profile/skills", headers=headers, json=add_payload)
    skill_id = add_res.json()["skill_id"]

    # Attach verified evidence
    evidence_payload = {
        "skill_id": skill_id,
        "source_type": "GITHUB",
        "source_id": "https://github.com/evidenceuser/yolo-vision",
        "evidence_text": "Trained custom YOLOv8 model for real-time defect classification in PyTorch.",
        "confidence": 0.95,
        "verified": True,
    }
    ev_res = await async_client.post("/api/v1/profile/skills/evidence", headers=headers, json=evidence_payload)
    assert ev_res.status_code == 201
    ev_data = ev_res.json()
    assert ev_data["verified"] is True
    assert ev_data["source_type"] == "GITHUB"
