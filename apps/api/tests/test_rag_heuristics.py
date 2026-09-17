import pytest
from app.services.rag_service import RagService


def test_recursive_semantic_chunker():
    """Verify recursive chunking splits long text into semantic chunks with overlap."""
    sample_text = """First major paragraph describing Google L5 distributed systems interviews.
It involves scalable architecture, Bigtable, Raft consensus, and consistent hashing.

Second paragraph detailing algorithmic coding.
Candidates must solve dynamic programming and graph problems within 45 minutes with optimal time complexity.

Third paragraph covering system scalability, caching with Redis, and data partitioning strategies."""

    chunks = RagService.chunk_text(sample_text, chunk_size=120, overlap=30)
    assert len(chunks) >= 2
    assert all(len(c) > 0 for c in chunks)
    # Check that key technical keywords are retained
    assert any("Google" in c or "distributed" in c for c in chunks)


def test_bm25_sparse_scoring_relevance():
    """Verify Okapi BM25 scoring rewards term frequency and penalizes irrelevant chunks."""
    query_terms = ["distributed", "raft", "consensus"]
    relevant_doc = ["distributed", "systems", "use", "raft", "consensus", "for", "fault", "tolerance"]
    irrelevant_doc = ["react", "nextjs", "css", "styling", "frontend", "buttons"]

    score_rel = RagService._compute_bm25_score(query_terms, relevant_doc, avg_doc_len=7.0)
    score_irrel = RagService._compute_bm25_score(query_terms, irrelevant_doc, avg_doc_len=7.0)

    assert score_rel > 2.0
    assert score_irrel == 0.0
