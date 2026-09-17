import pytest
from httpx import AsyncClient


async def get_test_auth_headers(async_client: AsyncClient, email: str = "jobadmin@placementos.ai") -> dict:
    reg_payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Job Admin",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_job_ingestion_and_deduplication_api(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client)

    # 1. Trigger first ingestion run (curated only for deterministic speed)
    ingest_payload = {
        "source_names": ["curated_placement"],
        "limit_per_source": 10,
    }
    res1 = await async_client.post("/api/v1/jobs/ingest", json=ingest_payload, headers=auth_headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total_inserted"] > 0
    assert data1["total_fetched"] == data1["total_inserted"]

    # 2. Trigger second ingestion run -> Must deduplicate
    res2 = await async_client.post("/api/v1/jobs/ingest", json=ingest_payload, headers=auth_headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["total_inserted"] == 0
    assert data2["total_duplicated"] > 0


@pytest.mark.asyncio
async def test_job_search_and_filters_api(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client, "filtertest@placementos.ai")

    # Ingest jobs first
    await async_client.post(
        "/api/v1/jobs/ingest",
        json={"source_names": ["curated_placement"]},
        headers=auth_headers,
    )

    # 1. List all jobs
    list_res = await async_client.get("/api/v1/jobs?page=1&page_size=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] > 0
    assert len(list_data["items"]) > 0

    first_job = list_data["items"][0]
    job_id = first_job["id"]
    assert len(first_job["skills"]) > 0

    # 2. Search keyword filter
    search_res = await async_client.get("/api/v1/jobs?search=Uber")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] >= 1
    assert any("Uber" in j["company"] for j in search_data["items"])

    # 3. Location type filter
    loc_res = await async_client.get("/api/v1/jobs?location_type=HYBRID")
    assert loc_res.status_code == 200
    loc_data = loc_res.json()
    assert loc_data["total"] > 0
    for j in loc_data["items"]:
        assert j["location_type"] == "HYBRID"

    # 4. Canonical skill filter
    skill_res = await async_client.get("/api/v1/jobs?skill=Python")
    assert skill_res.status_code == 200
    skill_data = skill_res.json()
    assert skill_data["total"] > 0
    for j in skill_data["items"]:
        skill_names = [s["name"] for s in j["skills"]]
        assert "Python" in skill_names

    # 5. Get Job by ID
    get_res = await async_client.get(f"/api/v1/jobs/{job_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["id"] == job_id
    assert "description" in detail
    assert "fingerprint" in detail
    assert len(detail["skills"]) > 0


@pytest.mark.asyncio
async def test_job_sources_telemetry_status_api(async_client: AsyncClient):
    auth_headers = await get_test_auth_headers(async_client, "telemetrytest@placementos.ai")

    # Ingest
    await async_client.post(
        "/api/v1/jobs/ingest",
        json={"source_names": ["curated_placement"]},
        headers=auth_headers,
    )

    # Telemetry
    status_res = await async_client.get("/api/v1/jobs/sources/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["total_active_jobs"] > 0
    assert len(status_data["sources"]) > 0

    curated_stat = next(
        (s for s in status_data["sources"] if s["source_name"] == "curated_placement"),
        None,
    )
    assert curated_stat is not None
    assert curated_stat["status"] == "SUCCESS"
    assert curated_stat["jobs_inserted"] > 0
