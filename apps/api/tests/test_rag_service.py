import pytest
from app.models.rag import RagSourceType
from app.schemas.rag import DocumentIngestRequest
from app.services.rag_service import RagService
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_rag_service_seed_and_hybrid_search():
    """Verify default seeding, hybrid vector + BM25 search, and RRF ranking."""
    async with TestingSessionLocal() as db_session:
        await RagService.ensure_seeded(db_session)

        # Search for Amazon leadership and DynamoDB
        results = await RagService.hybrid_search(
            db=db_session,
            query="Amazon leadership principles Customer Obsession DynamoDB",
            company="Amazon",
            limit=3,
            use_hybrid=True,
            use_reranking=True,
        )

        assert len(results) > 0
        top_result = results[0]
        assert "Amazon" in top_result.document_title or (top_result.company and "Amazon" in top_result.company)
        assert top_result.dense_score >= 0.0
        assert top_result.sparse_score > 0.0
        assert top_result.final_score > 0.0


@pytest.mark.asyncio
async def test_rag_service_grounded_query_and_citations():
    """Verify grounded answer synthesis with explicit source citations and graph entities."""
    async with TestingSessionLocal() as db_session:
        response = await RagService.answer_query(
            db=db_session,
            query="What are the main system design and coding topics at Google?",
            company="Google",
            top_k=2,
            include_graph=True,
        )

        assert response.query == "What are the main system design and coding topics at Google?"
        assert len(response.citations) > 0
        assert "Google" in response.citations[0].document_title or response.citations[0].company == "Google"
        assert "Takeaways" in response.answer or "Google" in response.answer
        assert response.retrieval_metadata["hybrid_search_enabled"] is True


@pytest.mark.asyncio
async def test_rag_service_document_ingest():
    """Verify custom placement guide ingestion with automatic chunking and indexing."""
    async with TestingSessionLocal() as db_session:
        ingest_req = DocumentIngestRequest(
            title="Stripe System Design & Idempotency Guide",
            source_type=RagSourceType.TECH_GUIDE.value,
            company="Stripe",
            role="Backend Infrastructure Engineer",
            difficulty="HARD",
            tags=["stripe", "idempotency", "payments", "distributed-locks"],
            raw_text="Stripe payment architecture requires strict idempotency keys stored in Redis with distributed locking via Redlock to prevent duplicate charges.",
        )

        doc = await RagService.ingest_document(db_session, ingest_req)
        assert doc.id is not None
        assert doc.title == "Stripe System Design & Idempotency Guide"
        assert doc.chunk_count >= 1

        # Search for the newly ingested document
        results = await RagService.hybrid_search(
            db=db_session,
            query="idempotency keys Stripe duplicate charges",
            company="Stripe",
            limit=2,
        )
        assert len(results) > 0
        assert results[0].document_id == doc.id
