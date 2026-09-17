import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_interview_api_full_workflow(async_client: AsyncClient):
    """Test full authenticated interview simulation API: create session, get active, respond to questions, get scorecard."""
    # 1. Register candidate user
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "interview_api_user@example.com",
            "password": "Password123!",
            "full_name": "API Interview Tester",
        },
    )
    assert reg_res.status_code == 201
    auth_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 2. Create 2-question interview session
    create_res = await async_client.post(
        "/api/v1/interviews/sessions/create",
        headers=headers,
        json={
            "interview_type": "TECHNICAL",
            "target_role": "Backend Engineer",
            "difficulty": "MEDIUM",
            "total_questions": 2,
        },
    )
    assert create_res.status_code == 201
    session_data = create_res.json()
    session_id = session_data["id"]
    assert session_data["total_questions"] == 2
    assert len(session_data["questions"]) == 2
    assert session_data["status"] == "IN_PROGRESS"

    # 3. Retrieve active session
    active_res = await async_client.get("/api/v1/interviews/sessions/active", headers=headers)
    assert active_res.status_code == 200
    assert active_res.json()["id"] == session_id

    # 4. Respond to Question 1
    resp1 = (
        "Situation: Our Postgres database was experiencing high latency on user queries. "
        "Task: I had to analyze execution plans and optimize indexing. "
        "Action: I ran EXPLAIN ANALYZE, identified a sequential scan on a 10M row table, and created a composite B-Tree index. "
        "Result: Query time dropped by 92% from 1.2s to 95ms."
    )
    turn1_res = await async_client.post(
        f"/api/v1/interviews/sessions/{session_id}/respond",
        headers=headers,
        json={"candidate_response_text": resp1},
    )
    assert turn1_res.status_code == 200
    turn1_data = turn1_res.json()
    assert turn1_data["turn_response"]["score"] >= 70.0
    assert turn1_data["is_session_completed"] is False
    assert turn1_data["next_question"] is not None

    # 5. Respond to Question 2 (Final question)
    resp2 = (
        "Situation: Our distributed cache required token bucket rate limiting at 100k QPS. "
        "Task: Design the rate limiter in Redis with zero race conditions. "
        "Action: I implemented atomic Lua scripts with Redis cluster sliding window counters. "
        "Result: Handled 120k QPS peak traffic with sub-3ms latency and 0 false throttling."
    )
    turn2_res = await async_client.post(
        f"/api/v1/interviews/sessions/{session_id}/respond",
        headers=headers,
        json={"candidate_response_text": resp2},
    )
    assert turn2_res.status_code == 200
    turn2_data = turn2_res.json()
    assert turn2_data["is_session_completed"] is True
    assert turn2_data["next_question"] is None

    # 6. Retrieve completed session scorecard
    detail_res = await async_client.get(f"/api/v1/interviews/sessions/{session_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["status"] == "COMPLETED"
    assert detail_data["overall_score"] is not None
    assert len(detail_data["responses"]) == 2
    assert len(detail_data["strengths"]) > 0

    # 7. List historical sessions
    list_res = await async_client.get("/api/v1/interviews/sessions", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


@pytest.mark.asyncio
async def test_interview_api_unauthorized_access(async_client: AsyncClient):
    """Verify unauthenticated access to interview session creation is rejected."""
    res = await async_client.post(
        "/api/v1/interviews/sessions/create",
        json={"target_role": "AI Engineer"},
    )
    assert res.status_code in [401, 403]
