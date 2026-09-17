from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    source_type: str = Field("COMPANY_ARCHIVE", description="COMPANY_ARCHIVE, SYLLABUS, INTERVIEW_TRANSCRIPT, TECH_GUIDE")
    company: Optional[str] = None
    role: Optional[str] = None
    difficulty: Optional[str] = "INTERMEDIATE"
    tags: List[str] = Field(default_factory=list)
    raw_text: str = Field(..., min_length=20)
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    id: str
    title: str
    source_type: str
    company: Optional[str] = None
    role: Optional[str] = None
    difficulty: Optional[str] = None
    tags: List[str]
    raw_text: Optional[str] = None
    chunk_count: int
    meta_info: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    company: Optional[str] = None
    source_type: Optional[str] = None
    limit: int = Field(5, ge=1, le=20)
    use_hybrid: bool = True
    use_reranking: bool = True


class RagSearchResultChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    company: Optional[str] = None
    source_type: str
    chunk_text: str
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rrf_score: float = 0.0
    final_score: float = 0.0


class RagSearchResponse(BaseModel):
    query: str
    total_chunks_matched: int
    results: List[RagSearchResultChunk]


class RagCitation(BaseModel):
    document_id: str
    document_title: str
    company: Optional[str] = None
    source_type: str
    chunk_index: int
    snippet: str


class RagGraphEntity(BaseModel):
    name: str
    node_type: str
    relation: str
    target: str


class RagQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    company: Optional[str] = None
    role: Optional[str] = None
    top_k: int = Field(4, ge=1, le=10)
    include_graph_context: bool = True


class RagQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[RagCitation]
    related_graph_entities: List[RagGraphEntity]
    retrieval_metadata: Dict[str, Any]


class GraphNodeDto(BaseModel):
    id: str
    name: str
    node_type: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class GraphEdgeDto(BaseModel):
    id: str
    source_node_id: str
    source_name: str
    target_node_id: str
    target_name: str
    relation_type: str
    weight: float
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphVisualizationResponse(BaseModel):
    nodes: List[GraphNodeDto]
    edges: List[GraphEdgeDto]
    total_nodes: int
    total_edges: int
