import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rag_api_documents_and_search(async_client: AsyncClient):
    """Verify listing documents, hybrid search, and knowledge graph endpoints via REST API."""
    # 1. List pre-seeded documents
    list_res = await async_client.get("/api/v1/rag/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) >= 5
    assert any(d["company"] == "Google" for d in docs)

    # 2. Perform Hybrid Search
    search_payload = {
        "query": "Operating Systems Virtual Memory Paging Concurrency",
        "limit": 3,
        "use_hybrid": True,
        "use_reranking": True,
    }
    search_res = await async_client.post("/api/v1/rag/search", json=search_payload)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total_chunks_matched"] > 0
    assert len(search_data["results"]) > 0
    assert "Operating Systems" in search_data["results"][0]["document_title"] or "Syllabus" in search_data["results"][0]["document_title"]

    # 3. Perform RAG Grounded Query
    query_payload = {
        "query": "How to clear Amazon Leadership Principles rounds?",
        "company": "Amazon",
        "top_k": 3,
        "include_graph_context": True,
    }
    query_res = await async_client.post("/api/v1/rag/query", json=query_payload)
    assert query_res.status_code == 200
    query_data = query_res.json()
    assert "Amazon" in query_data["answer"]
    assert len(query_data["citations"]) > 0

    # 4. Fetch Knowledge Graph Visualization
    graph_res = await async_client.get("/api/v1/rag/graph")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert graph_data["total_nodes"] > 0
    assert graph_data["total_edges"] > 0
    assert any(n["name"] == "Google" for n in graph_data["nodes"])


@pytest.mark.asyncio
async def test_rag_api_document_ingestion_authenticated(async_client: AsyncClient):
    """Verify document ingestion requires authentication."""
    # Register test user
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "rag_tester@example.com",
            "password": "Password123!",
            "full_name": "RAG Tester",
        },
    )
    assert reg_res.status_code == 201
    auth_token = reg_res.json()["access_token"]

    ingest_payload = {
        "title": "Netflix Chaos Engineering & Microservices",
        "source_type": "COMPANY_ARCHIVE",
        "company": "Netflix",
        "role": "Site Reliability Engineer",
        "difficulty": "HARD",
        "tags": ["netflix", "chaos-engineering", "microservices"],
        "raw_text": "Netflix validates high availability through Chaos Monkey and Simian Army, injecting random instance failures in AWS EC2.",
    }

    # Unauthenticated should fail
    unauth_res = await async_client.post("/api/v1/rag/documents", json=ingest_payload)
    assert unauth_res.status_code in [401, 403]

    # Authenticated should succeed
    auth_res = await async_client.post(
        "/api/v1/rag/documents",
        json=ingest_payload,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert auth_res.status_code == 201
    doc = auth_res.json()
    assert doc["title"] == "Netflix Chaos Engineering & Microservices"
    assert doc["company"] == "Netflix"
    assert doc["chunk_count"] >= 1
