# Phase 10: Hybrid RAG & Knowledge Graph Engine — Walkthrough

## Overview
Phase 10 implements the enterprise-grade **Hybrid RAG & Knowledge Graph Engine** for AI PlacementOS. It powers intelligent context retrieval, semantic search, and grounded Q&A across curated FAANG+ placement archives, campus recruitment syllabi, and technical interview transcripts.

### Key Architectural Capabilities
1. **Multi-Stage Hybrid Retrieval Pipeline**:
   - **Dense Semantic Vector Search** (128-d domain-projected embeddings using cosine similarity).
   - **Sparse Keyword Matcher** (Okapi BM25 with term frequency, inverse document frequency $IDF$, and length normalization).
   - **Reciprocal Rank Fusion (RRF)** ($k=60$) combining dense and sparse rank distributions.
   - **Cross-Encoder Contextual Re-ranker** applying query-to-chunk exact phrase bonus, keyword density, and company metadata alignment.
2. **Knowledge Graph Triplet Ontology**:
   - Entity nodes (`COMPANY`, `TOPIC`, `QUESTION_PATTERN`, `ROLE`).
   - Relational edges (`TESTS_SKILL`, `COMMONLY_ASKED_AT`, `PREREQUISITE_OF`, `REQUIRES_PATTERN`, `PART_OF_ROUND`).
   - Multi-hop graph traversal contextualizing student queries with connected curriculum topics.
3. **Curated Placement Corpus**:
   - Google L4/L5 Distributed Systems & ML Systems Design.
   - Amazon Leadership Principles (STAR method) & High-Throughput Microservices.
   - Meta High-Velocity Live Coding Patterns & Distributed Caching.
   - Core Computer Science Placement Syllabus (OS, DBMS, Computer Networks).
   - Microsoft Azure Cloud Enterprise Systems Design.
4. **Grounded Synthesis with Explicit Citations**:
   - Generates answers strictly grounded in retrieved chunks with clickable source citation cards.

---

## Verification Results

### Backend Pytest Suite
- **90/90 tests passing** across the entire backend:
  - `tests/test_rag_heuristics.py`
  - `tests/test_rag_service.py`
  - `tests/test_rag_api.py`

### Next.js Production Build
- `npm run build` compiled 16/16 routes with 0 errors.
- New route `/knowledge` prerendered with full interactive UI (GraphRAG assistant, hybrid search inspector, graph explorer, corpus viewer, and document ingestion).
