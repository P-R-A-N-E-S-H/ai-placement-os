from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.models.rag import (
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    RagDocument,
)
from app.models.user import User
from app.schemas.rag import (
    DocumentIngestRequest,
    DocumentResponse,
    GraphEdgeDto,
    GraphNodeDto,
    GraphVisualizationResponse,
    RagQueryRequest,
    RagQueryResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from app.services.rag_service import RagService

router = APIRouter()


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    company: Optional[str] = Query(None, description="Filter by company"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> List[DocumentResponse]:
    """List placement corpus documents with optional filters."""
    await RagService.ensure_seeded(db)

    stmt = select(RagDocument).order_by(RagDocument.created_at.desc()).limit(limit)
    if source_type:
        stmt = stmt.where(RagDocument.source_type == source_type)
    if company:
        stmt = stmt.where(RagDocument.company.ilike(f"%{company}%"))

    result = await db.execute(stmt)
    docs = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    request: DocumentIngestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """Ingest a new placement document with recursive semantic chunking and dense vector indexing."""
    doc = await RagService.ingest_document(db, request)
    return DocumentResponse.model_validate(doc)


@router.post("/search", response_model=RagSearchResponse)
async def hybrid_search(
    request: RagSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> RagSearchResponse:
    """
    Perform multi-stage Hybrid Search:
    1. Dense Cosine Similarity Semantic Vector Match
    2. Okapi BM25 Sparse Keyword Match
    3. Reciprocal Rank Fusion (RRF k=60)
    4. Cross-Encoder Contextual Re-ranking
    """
    results = await RagService.hybrid_search(
        db=db,
        query=request.query,
        company=request.company,
        source_type=request.source_type,
        limit=request.limit,
        use_hybrid=request.use_hybrid,
        use_reranking=request.use_reranking,
    )
    return RagSearchResponse(
        query=request.query,
        total_chunks_matched=len(results),
        results=results,
    )


@router.post("/query", response_model=RagQueryResponse)
async def rag_query_answer(
    request: RagQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> RagQueryResponse:
    """
    Query the Placement Knowledge Hub with GraphRAG synthesis and explicit source citations.
    """
    return await RagService.answer_query(
        db=db,
        query=request.query,
        company=request.company,
        role=request.role,
        top_k=request.top_k,
        include_graph=request.include_graph_context,
    )


@router.get("/graph", response_model=GraphVisualizationResponse)
async def get_knowledge_graph(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> GraphVisualizationResponse:
    """Retrieve full Knowledge Graph nodes and edges for visualization and concept exploration."""
    await RagService.ensure_seeded(db)

    nodes_res = await db.execute(select(KnowledgeGraphNode))
    nodes = list(nodes_res.scalars().all())

    edges_res = await db.execute(
        select(KnowledgeGraphEdge).options(
            selectinload(KnowledgeGraphEdge.source_node),
            selectinload(KnowledgeGraphEdge.target_node),
        )
    )
    edges = list(edges_res.scalars().all())

    node_dtos = [GraphNodeDto.model_validate(n) for n in nodes]
    edge_dtos = [
        GraphEdgeDto(
            id=e.id,
            source_node_id=e.source_node_id,
            source_name=e.source_node.name if e.source_node else "Unknown",
            target_node_id=e.target_node_id,
            target_name=e.target_node.name if e.target_node else "Unknown",
            relation_type=e.relation_type,
            weight=e.weight,
            properties=e.properties,
        )
        for e in edges
    ]

    return GraphVisualizationResponse(
        nodes=node_dtos,
        edges=edge_dtos,
        total_nodes=len(node_dtos),
        total_edges=len(edge_dtos),
    )
