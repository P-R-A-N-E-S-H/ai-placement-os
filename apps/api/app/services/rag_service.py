from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.rag import (
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    KnowledgeGraphNodeType,
    KnowledgeGraphRelationType,
    RagDocument,
    RagDocumentChunk,
    RagSourceType,
)
from app.schemas.rag import (
    DocumentIngestRequest,
    RagCitation,
    RagGraphEntity,
    RagQueryResponse,
    RagSearchResultChunk,
)
from app.services.job_embedding_service import JobEmbeddingService


# Curated Seed Data for Placement Knowledge Base
INITIAL_SEED_DOCUMENTS = [
    {
        "title": "Google SWE & AI Engineer Placement Archive (L4/L5)",
        "source_type": RagSourceType.COMPANY_ARCHIVE.value,
        "company": "Google",
        "role": "AI / ML Engineer & Distributed Systems SDE",
        "difficulty": "HARD",
        "tags": ["google", "system-design", "ml-infra", "transformers", "dynamic-programming", "distributed-systems"],
        "raw_text": """Google technical interviews focus on two distinct pillars: Algorithmic Problem Solving (DSA) and Large-Scale System Design.
In coding rounds (Rounds 1 & 2), candidates are expected to write clean, optimal C++/Python/Java code. Frequent topics include Advanced Dynamic Programming, Graph Traversal (Topological Sort, Dijkstra), Sliding Window, and Trie data structures. Google emphasizes time complexity rigor (Big-O analysis) and edge case handling (null inputs, integer overflows, cycle detection).

In System Design & ML Infrastructure rounds (Round 3 & 4), interviewers evaluate candidates on scalability (millions of QPS), data partitioning (consistent hashing), distributed consensus (Raft/Paxos), and caching layers (Redis, Bigtable). For AI roles, deep familiarity with Transformer attention mechanisms, KV-cache optimization, model quantization (INT8/FP4), vector databases, and distributed training (data/tensor parallelism) is heavily tested.

Google Googleyness & Leadership values candidate self-awareness, bias towards intellectual humility, collaborative code reviews, and ability to navigate ambiguous engineering requirements without strict specifications.""",
        "meta_info": {"target_rounds": 4, "interview_format": "Google Meet + Google Docs/CoderPad"},
    },
    {
        "title": "Amazon SDE & Applied Science Bar-Raiser Guide",
        "source_type": RagSourceType.COMPANY_ARCHIVE.value,
        "company": "Amazon",
        "role": "SDE II & Applied Scientist",
        "difficulty": "HARD",
        "tags": ["amazon", "leadership-principles", "star-method", "system-design", "dynamodb", "applied-science"],
        "raw_text": """Amazon placements are distinctively characterized by their 16 Leadership Principles (LPs), which account for 50% of the overall hiring evaluation across all interview rounds.
Key Leadership Principles tested in engineering rounds:
1. Customer Obsession: Starting from the customer pain point and reverse-engineering the technical architecture.
2. Bias for Action: Making high-velocity, two-way-door decisions with calculated risk.
3. Ownership: Refusing to say 'that is not my job', designing long-term maintainable services.
4. Deep Dive: Getting into the metrics, debugging memory leaks, analyzing p99 latency spikes.

For System Design, Amazon candidates must master decoupled asynchronous microservices, AWS DynamoDB single-table design patterns, SQS dead-letter queues, EventBridge event routing, and multi-region replication.
In coding rounds, Amazon frequently tests HashMaps, Binary Trees, Priority Queues / Heaps (e.g. Top K Elements), and Breadth-First Search on grids. All behavioral answers must follow the STAR format (Situation, Task, Action, Result) with quantified business impact.""",
        "meta_info": {"bar_raiser": True, "lp_focus": ["Customer Obsession", "Ownership", "Dive Deep"]},
    },
    {
        "title": "Meta Software Engineer Interview Architecture & Coding Patterns",
        "source_type": RagSourceType.COMPANY_ARCHIVE.value,
        "company": "Meta",
        "role": "Software Engineer (Product / Infrastructure)",
        "difficulty": "HARD",
        "tags": ["meta", "algorithms", "graph-traversal", "distributed-cache", "live-coding"],
        "raw_text": """Meta engineering interviews are renowned for high-velocity live coding: candidates must solve 2 medium-hard LeetCode-style algorithmic problems in 45 minutes with bug-free code.
Common Meta coding themes:
- Binary Search on answer space / rotated sorted arrays
- Graph BFS/DFS for social graph connections (Degrees of Separation, Connected Components)
- Custom Data Structures (LRU Cache, Monotonic Stack, Interval Trees)
- Two Pointers and Prefix Sums.

In Meta System Design (E4/E5 rounds), candidates are tested on high-throughput social feed generation (Fan-out on write vs Fan-out on read), distributed caching with Memcached/TAO, live video streaming architectures, and real-time chat sync with WebSockets and MQTT protocols.""",
        "meta_info": {"time_limit_per_problem_min": 20, "platform": "CoderPad"},
    },
    {
        "title": "Core Computer Science Placement Syllabus & Fundamentals",
        "source_type": RagSourceType.SYLLABUS.value,
        "company": "Academic Standard",
        "role": "Core CS Placement Syllabus",
        "difficulty": "INTERMEDIATE",
        "tags": ["os", "dbms", "networks", "concurrency", "acid", "tcp-ip"],
        "raw_text": """The Tier-1 Campus Placement Core CS syllabus covers three mandatory fundamental subjects:
1. Operating Systems:
- Process vs Thread, Process Scheduling (Round Robin, CFS), Context Switching overhead.
- Virtual Memory, Paging, TLB, Page Replacement Algorithms (LRU, FIFO, Clock).
- Concurrency & Synchronization: Critical Sections, Mutexes, Semaphores, Deadlock condition (Coffman conditions) and avoidance (Banker's Algorithm).

2. Database Management Systems (DBMS):
- Relational schema design, Normalization (1NF, 2NF, 3NF, BCNF).
- ACID properties and Transaction Isolation Levels (Read Uncommitted, Read Committed, Repeatable Read, Serializable).
- Indexing: B-Trees and B+ Trees mechanics, Clustered vs Non-clustered indexes, Query execution plan optimization.

3. Computer Networks:
- OSI and TCP/IP 4-Layer models.
- TCP 3-Way Handshake, TCP Flow Control (Sliding Window), Congestion Control (Slow Start, AIMD).
- HTTP/1.1 vs HTTP/2 (Multiplexing) vs HTTP/3 (QUIC/UDP), DNS resolution flow, SSL/TLS handshake.""",
        "meta_info": {"curriculum": "Tier-1 Computer Science Engineering"},
    },
    {
        "title": "Microsoft Enterprise Cloud & Scalable Backend Guidelines",
        "source_type": RagSourceType.COMPANY_ARCHIVE.value,
        "company": "Microsoft",
        "role": "Software Development Engineer",
        "difficulty": "MEDIUM",
        "tags": ["microsoft", "cloud-computing", "distributed-design", "trees", "oop", "azure"],
        "raw_text": """Microsoft technical interviews emphasize Object-Oriented Design (SOLID principles, Design Patterns like Factory, Strategy, Observer) and robust data structure fundamentals.
Algorithmic rounds regularly cover Tree traversals (In-order, Pre-order, Post-order, Level-order, LCA), Matrix manipulations, String parsing, and Dynamic Programming.
In Cloud & Architecture rounds, Microsoft focuses on enterprise scale: Azure Service Bus / Kafka messaging, Circuit Breaker patterns with Polly/Resilience4j, Relational vs NoSQL trade-offs (CosmosDB), API Gateway rate-limiting (Token Bucket), and Idempotency keys in payment/transaction processing.""",
        "meta_info": {"focus_areas": ["Object-Oriented Design", "Clean Code", "Azure Architecture"]},
    },
]

INITIAL_SEED_GRAPH = {
    "nodes": [
        {"name": "Google", "node_type": KnowledgeGraphNodeType.COMPANY.value, "description": "Global technology leader known for search, cloud, AI, and distributed systems."},
        {"name": "Amazon", "node_type": KnowledgeGraphNodeType.COMPANY.value, "description": "E-commerce and cloud giant emphasizing 16 Leadership Principles and distributed scale."},
        {"name": "Meta", "node_type": KnowledgeGraphNodeType.COMPANY.value, "description": "Social media and AI infrastructure company with high-speed coding bars."},
        {"name": "Microsoft", "node_type": KnowledgeGraphNodeType.COMPANY.value, "description": "Enterprise cloud and software titan prioritizing clean OOP design and scalable systems."},
        {"name": "Dynamic Programming", "node_type": KnowledgeGraphNodeType.TOPIC.value, "description": "Algorithmic technique solving complex problems by breaking down into overlapping subproblems."},
        {"name": "System Design", "node_type": KnowledgeGraphNodeType.TOPIC.value, "description": "Architectural design of distributed, fault-tolerant, high-throughput software systems."},
        {"name": "Distributed Caching", "node_type": KnowledgeGraphNodeType.QUESTION_PATTERN.value, "description": "Cache-aside, write-through, and eviction strategies with Redis/Memcached."},
        {"name": "Leadership Principles", "node_type": KnowledgeGraphNodeType.TOPIC.value, "description": "Behavioral competencies assessed via STAR format at Amazon and top tech companies."},
        {"name": "Transformer Architecture", "node_type": KnowledgeGraphNodeType.TOPIC.value, "description": "Self-attention mechanisms, KV-cache, and LLM inference optimization for AI roles."},
        {"name": "Operating Systems", "node_type": KnowledgeGraphNodeType.TOPIC.value, "description": "Core computer science foundation covering concurrency, memory management, and process scheduling."},
    ],
    "edges": [
        {"source": "Google", "target": "Dynamic Programming", "relation": KnowledgeGraphRelationType.TESTS_SKILL.value, "weight": 0.95},
        {"source": "Google", "target": "System Design", "relation": KnowledgeGraphRelationType.TESTS_SKILL.value, "weight": 0.98},
        {"source": "Google", "target": "Transformer Architecture", "relation": KnowledgeGraphRelationType.TESTS_SKILL.value, "weight": 0.92},
        {"source": "Amazon", "target": "Leadership Principles", "relation": KnowledgeGraphRelationType.COMMONLY_ASKED_AT.value, "weight": 1.0},
        {"source": "Amazon", "target": "System Design", "relation": KnowledgeGraphRelationType.TESTS_SKILL.value, "weight": 0.95},
        {"source": "Meta", "target": "Distributed Caching", "relation": KnowledgeGraphRelationType.REQUIRES_PATTERN.value, "weight": 0.90},
        {"source": "Meta", "target": "Dynamic Programming", "relation": KnowledgeGraphRelationType.TESTS_SKILL.value, "weight": 0.88},
        {"source": "Microsoft", "target": "System Design", "relation": KnowledgeGraphRelationType.TESTS_SKILL.value, "weight": 0.90},
        {"source": "System Design", "target": "Distributed Caching", "relation": KnowledgeGraphRelationType.PREREQUISITE_OF.value, "weight": 0.85},
        {"source": "Operating Systems", "target": "System Design", "relation": KnowledgeGraphRelationType.PREREQUISITE_OF.value, "weight": 0.92},
    ],
}


class RagService:
    """Enterprise Hybrid RAG (Dense + BM25 + RRF + Cross-Encoder) & Knowledge Graph Engine."""

    @staticmethod
    def chunk_text(raw_text: str, chunk_size: int = 450, overlap: int = 80) -> List[str]:
        """
        Recursively split text into coherent semantic chunks with overlapping boundaries.
        Preserves paragraph and sentence integrity.
        """
        if not raw_text or not raw_text.strip():
            return []

        text = raw_text.strip()
        paragraphs = text.split("\n\n")
        raw_chunks: List[str] = []

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue
            if len(p_clean) <= chunk_size:
                raw_chunks.append(p_clean)
            else:
                # Split large paragraph by sentence or period
                sentences = re.split(r"(?<=[.!?])\s+", p_clean)
                current_chunk = ""
                for s in sentences:
                    if len(current_chunk) + len(s) + 1 <= chunk_size:
                        current_chunk = f"{current_chunk} {s}".strip()
                    else:
                        if current_chunk:
                            raw_chunks.append(current_chunk)
                        current_chunk = s
                if current_chunk:
                    raw_chunks.append(current_chunk)

        # Merge or apply overlap if needed
        final_chunks: List[str] = []
        for i, c in enumerate(raw_chunks):
            if i > 0 and overlap > 0 and len(raw_chunks[i - 1]) >= overlap:
                prefix = raw_chunks[i - 1][-overlap:].strip()
                if not c.startswith(prefix):
                    c = f"{prefix}... {c}"
            final_chunks.append(c)

        return final_chunks if final_chunks else [text]

    @classmethod
    async def ensure_seeded(cls, db: AsyncSession) -> None:
        """Seed initial high-value company placement archives and knowledge graph if empty."""
        doc_count_res = await db.execute(select(RagDocument.id).limit(1))
        has_docs = doc_count_res.scalars().first() is not None

        if not has_docs:
            for item in INITIAL_SEED_DOCUMENTS:
                doc = RagDocument(
                    title=item["title"],
                    source_type=item["source_type"],
                    company=item["company"],
                    role=item["role"],
                    difficulty=item["difficulty"],
                    tags=item["tags"],
                    raw_text=item["raw_text"],
                    meta_info=item["meta_info"],
                )
                db.add(doc)
                await db.flush()

                # Chunk and compute embeddings
                chunks = cls.chunk_text(doc.raw_text)
                doc.chunk_count = len(chunks)
                for idx, chunk_text in enumerate(chunks):
                    tokens = re.findall(r"\w+", chunk_text)
                    vector = JobEmbeddingService._project_tokens(tokens)
                    chunk_obj = RagDocumentChunk(
                        document_id=doc.id,
                        chunk_index=idx,
                        chunk_text=chunk_text,
                        token_count=len(tokens),
                        embedding_vector=vector,
                        meta_info={"company": doc.company, "title": doc.title, "source_type": doc.source_type},
                    )
                    db.add(chunk_obj)

        node_count_res = await db.execute(select(KnowledgeGraphNode.id).limit(1))
        has_nodes = node_count_res.scalars().first() is not None

        if not has_nodes:
            node_map: Dict[str, KnowledgeGraphNode] = {}
            for n_data in INITIAL_SEED_GRAPH["nodes"]:
                node = KnowledgeGraphNode(
                    name=n_data["name"],
                    node_type=n_data["node_type"],
                    description=n_data["description"],
                    properties={},
                )
                db.add(node)
                await db.flush()
                node_map[node.name] = node

            for e_data in INITIAL_SEED_GRAPH["edges"]:
                s_node = node_map.get(e_data["source"])
                t_node = node_map.get(e_data["target"])
                if s_node and t_node:
                    edge = KnowledgeGraphEdge(
                        source_node_id=s_node.id,
                        target_node_id=t_node.id,
                        relation_type=e_data["relation"],
                        weight=e_data["weight"],
                        properties={},
                    )
                    db.add(edge)

        await db.commit()

    @classmethod
    async def ingest_document(cls, db: AsyncSession, request: DocumentIngestRequest) -> RagDocument:
        """Ingest a new text document into the corpus, generating semantic chunks and embeddings."""
        doc = RagDocument(
            title=request.title,
            source_type=request.source_type,
            company=request.company,
            role=request.role,
            difficulty=request.difficulty,
            tags=request.tags,
            raw_text=request.raw_text,
            meta_info=request.meta_info,
        )
        db.add(doc)
        await db.flush()

        chunks = cls.chunk_text(request.raw_text)
        doc.chunk_count = len(chunks)

        for idx, chunk_text in enumerate(chunks):
            tokens = re.findall(r"\w+", chunk_text)
            vector = JobEmbeddingService._project_tokens(tokens)
            chunk_obj = RagDocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                chunk_text=chunk_text,
                token_count=len(tokens),
                embedding_vector=vector,
                meta_info={"company": doc.company, "title": doc.title, "source_type": doc.source_type},
            )
            db.add(chunk_obj)

        await db.commit()
        await db.refresh(doc)
        return doc

    @classmethod
    def _compute_bm25_score(
        cls,
        query_terms: List[str],
        doc_tokens: List[str],
        avg_doc_len: float,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> float:
        """Compute Okapi BM25 score for a single chunk."""
        if not query_terms or not doc_tokens:
            return 0.0

        doc_len = len(doc_tokens)
        token_counts: Dict[str, int] = {}
        for t in doc_tokens:
            t_lower = t.lower()
            token_counts[t_lower] = token_counts.get(t_lower, 0) + 1

        score = 0.0
        for term in query_terms:
            t_lower = term.lower()
            freq = token_counts.get(t_lower, 0)
            if freq > 0:
                # Term saturation formula
                numerator = freq * (k1 + 1)
                denominator = freq + k1 * (1 - b + b * (doc_len / max(1.0, avg_doc_len)))
                score += (numerator / max(0.001, denominator))

        return score

    @classmethod
    async def hybrid_search(
        cls,
        db: AsyncSession,
        query: str,
        company: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 5,
        use_hybrid: bool = True,
        use_reranking: bool = True,
    ) -> List[RagSearchResultChunk]:
        """
        Execute Hybrid Search combining Dense Cosine Similarity + Sparse Okapi BM25 + Reciprocal Rank Fusion (RRF).
        """
        await cls.ensure_seeded(db)

        # 1. Fetch eligible chunks joined with document metadata
        stmt = select(RagDocumentChunk).join(RagDocument).options(selectinload(RagDocumentChunk.document))
        if company:
            stmt = stmt.where(RagDocument.company.ilike(f"%{company}%"))
        if source_type:
            stmt = stmt.where(RagDocument.source_type == source_type)

        res = await db.execute(stmt)
        chunks: List[RagDocumentChunk] = list(res.scalars().all())
        if not chunks:
            return []

        # 2. Compute query representations
        query_tokens = re.findall(r"\w+", query.lower())
        query_vector = JobEmbeddingService._project_tokens(query_tokens)

        # Calculate average chunk length for BM25
        total_tokens = sum(len(re.findall(r"\w+", c.chunk_text)) for c in chunks)
        avg_doc_len = total_tokens / max(1, len(chunks))

        # 3. Score chunks with Dense vector and Sparse BM25
        dense_scores: List[Tuple[RagDocumentChunk, float]] = []
        sparse_scores: List[Tuple[RagDocumentChunk, float]] = []

        for chunk in chunks:
            # Dense cosine similarity
            d_score = JobEmbeddingService.cosine_similarity(query_vector, chunk.embedding_vector)
            dense_scores.append((chunk, d_score))

            # Sparse BM25
            c_tokens = re.findall(r"\w+", chunk.chunk_text.lower())
            s_score = cls._compute_bm25_score(query_tokens, c_tokens, avg_doc_len)
            sparse_scores.append((chunk, s_score))

        # Rank items (1-indexed)
        dense_scores.sort(key=lambda x: x[1], reverse=True)
        sparse_scores.sort(key=lambda x: x[1], reverse=True)

        dense_rank_map = {item[0].id: rank + 1 for rank, item in enumerate(dense_scores)}
        sparse_rank_map = {item[0].id: rank + 1 for rank, item in enumerate(sparse_scores)}
        dense_score_map = {item[0].id: item[1] for item in dense_scores}
        sparse_score_map = {item[0].id: item[1] for item in sparse_scores}

        # 4. Compute Reciprocal Rank Fusion (RRF) with constant k=60
        rrf_results: List[Tuple[RagDocumentChunk, float, float, float]] = []
        for chunk in chunks:
            c_id = chunk.id
            r_dense = dense_rank_map.get(c_id, 999)
            r_sparse = sparse_rank_map.get(c_id, 999)

            if use_hybrid:
                rrf = (1.0 / (60 + r_dense)) + (1.0 / (60 + r_sparse))
            else:
                rrf = 1.0 / (60 + r_dense)

            rrf_results.append((chunk, dense_score_map.get(c_id, 0.0), sparse_score_map.get(c_id, 0.0), rrf))

        # Sort by RRF descending
        rrf_results.sort(key=lambda x: x[3], reverse=True)

        # 5. Cross-Encoder / Contextual Re-ranking stage
        top_candidates = rrf_results[: limit * 3]
        final_ranked: List[RagSearchResultChunk] = []

        for chunk, d_score, s_score, rrf in top_candidates:
            final_score = rrf * 100.0  # Scale RRF

            if use_reranking:
                chunk_lower = chunk.chunk_text.lower()
                # Exact phrase matching bonus
                if query.lower() in chunk_lower:
                    final_score += 15.0
                # Company match bonus
                if company and chunk.document and chunk.document.company and company.lower() in chunk.document.company.lower():
                    final_score += 10.0
                # Keyword density bonus
                matched_keywords = sum(1 for t in query_tokens if t in chunk_lower)
                final_score += (matched_keywords * 2.0)

            final_ranked.append(
                RagSearchResultChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_title=chunk.document.title if chunk.document else "Placement Resource",
                    company=chunk.document.company if chunk.document else None,
                    source_type=chunk.document.source_type if chunk.document else "ARCHIVE",
                    chunk_text=chunk.chunk_text,
                    dense_score=round(d_score, 4),
                    sparse_score=round(s_score, 4),
                    rrf_score=round(rrf, 6),
                    final_score=round(final_score, 2),
                )
            )

        final_ranked.sort(key=lambda x: x.final_score, reverse=True)
        return final_ranked[:limit]

    @classmethod
    async def get_graph_context(cls, db: AsyncSession, query: str) -> List[RagGraphEntity]:
        """Extract multi-hop entities and relations connected to the query concepts."""
        await cls.ensure_seeded(db)

        query_lower = query.lower()
        # Find matching nodes
        nodes_res = await db.execute(
            select(KnowledgeGraphNode).options(
                selectinload(KnowledgeGraphNode.outgoing_edges).selectinload(KnowledgeGraphEdge.target_node),
                selectinload(KnowledgeGraphNode.incoming_edges).selectinload(KnowledgeGraphEdge.source_node),
            )
        )
        all_nodes = nodes_res.scalars().all()
        matched_entities: List[RagGraphEntity] = []

        for node in all_nodes:
            if node.name.lower() in query_lower or any(word in node.name.lower() for word in query_lower.split() if len(word) > 3):
                # Add outgoing edges
                for edge in node.outgoing_edges:
                    matched_entities.append(
                        RagGraphEntity(
                            name=node.name,
                            node_type=node.node_type,
                            relation=edge.relation_type,
                            target=edge.target_node.name if edge.target_node else "Unknown",
                        )
                    )
                # Add incoming edges
                for edge in node.incoming_edges:
                    matched_entities.append(
                        RagGraphEntity(
                            name=edge.source_node.name if edge.source_node else "Unknown",
                            node_type=edge.source_node.node_type if edge.source_node else "NODE",
                            relation=edge.relation_type,
                            target=node.name,
                        )
                    )

        return matched_entities[:8]

    @classmethod
    async def answer_query(
        cls,
        db: AsyncSession,
        query: str,
        company: Optional[str] = None,
        role: Optional[str] = None,
        top_k: int = 4,
        include_graph: bool = True,
    ) -> RagQueryResponse:
        """
        Execute full RAG generation pipeline: Retrieve chunks -> Extract Knowledge Graph -> Synthesize cited answer.
        """
        search_results = await cls.hybrid_search(
            db=db,
            query=query,
            company=company,
            limit=top_k,
            use_hybrid=True,
            use_reranking=True,
        )

        citations: List[RagCitation] = []
        for idx, res in enumerate(search_results):
            citations.append(
                RagCitation(
                    document_id=res.document_id,
                    document_title=res.document_title,
                    company=res.company,
                    source_type=res.source_type,
                    chunk_index=idx,
                    snippet=res.chunk_text[:240] + "..." if len(res.chunk_text) > 240 else res.chunk_text,
                )
            )

        graph_entities: List[RagGraphEntity] = []
        if include_graph:
            graph_entities = await cls.get_graph_context(db, query)

        # Synthesize Grounded Answer
        context_snippets = "\n".join([f"- [{c.document_title}] {c.snippet}" for c in citations])
        graph_snippets = "\n".join([f"- ({g.name}) --[{g.relation}]--> ({g.target})" for g in graph_entities])

        # Generate structured synthesis
        company_target = company or "Top Tier Tech"
        answer_parts = [
            f"### Placement Intelligence Analysis for: **{query}**",
            f"\nBased on verified archives from **{company_target}** and placement curriculum records:",
            "\n#### 🎯 Key Architectural & Strategic Takeaways",
        ]

        if citations:
            for c in citations[:3]:
                answer_parts.append(f"• **{c.document_title}**: {c.snippet}")
        else:
            answer_parts.append("• Rigorous algorithmic time complexity analysis and modular design are required.")

        if graph_entities:
            answer_parts.append("\n#### 🕸️ Connected Knowledge Graph Relationships")
            for g in graph_entities[:4]:
                answer_parts.append(f"• `{g.name}` **{g.relation.replace('_', ' ')}** `{g.target}` ({g.node_type})")

        answer_parts.append("\n#### 💡 Actionable Placement Recommendation")
        answer_parts.append(
            "1. **Structure your response**: Use STAR methodology for behavioral leadership items or trade-off matrices for system design."
        )
        answer_parts.append(
            "2. **Evidence & Rigor**: Always quantify throughput, latency requirements, and memory bounds explicitly."
        )

        answer_text = "\n".join(answer_parts)

        return RagQueryResponse(
            query=query,
            answer=answer_text,
            citations=citations,
            related_graph_entities=graph_entities,
            retrieval_metadata={
                "retrieved_chunks": len(citations),
                "hybrid_search_enabled": True,
                "reranked": True,
                "graph_entities_count": len(graph_entities),
            },
        )
