from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class RagSourceType(str, enum.Enum):
    COMPANY_ARCHIVE = "COMPANY_ARCHIVE"
    SYLLABUS = "SYLLABUS"
    INTERVIEW_TRANSCRIPT = "INTERVIEW_TRANSCRIPT"
    TECH_GUIDE = "TECH_GUIDE"


class RagDocument(Base, UUIDMixin, TimestampMixin):
    """Corpus document containing interview archives, syllabus, or technical guides."""
    __tablename__ = "rag_documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, default=RagSourceType.COMPANY_ARCHIVE.value, index=True)
    company: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    role: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, default="INTERMEDIATE")
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meta_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    chunks: Mapped[List[RagDocumentChunk]] = relationship(
        "RagDocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="RagDocumentChunk.chunk_index",
    )


class RagDocumentChunk(Base, UUIDMixin, TimestampMixin):
    """Semantic chunk extracted from a RagDocument with precomputed dense embeddings."""
    __tablename__ = "rag_document_chunks"

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("rag_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_vector: Mapped[List[float]] = mapped_column(JSON, default=list, nullable=False)
    meta_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    document: Mapped[RagDocument] = relationship("RagDocument", back_populates="chunks")


class KnowledgeGraphNodeType(str, enum.Enum):
    COMPANY = "COMPANY"
    TOPIC = "TOPIC"
    SKILL = "SKILL"
    ROLE = "ROLE"
    QUESTION_PATTERN = "QUESTION_PATTERN"
    ROUND_TYPE = "ROUND_TYPE"


class KnowledgeGraphRelationType(str, enum.Enum):
    TESTS_SKILL = "TESTS_SKILL"
    COMMONLY_ASKED_AT = "COMMONLY_ASKED_AT"
    PREREQUISITE_OF = "PREREQUISITE_OF"
    PART_OF_ROUND = "PART_OF_ROUND"
    REQUIRES_PATTERN = "REQUIRES_PATTERN"
    BELONGS_TO_TOPIC = "BELONGS_TO_TOPIC"


class KnowledgeGraphNode(Base, UUIDMixin, TimestampMixin):
    """Entity node in the Placement Knowledge Graph."""
    __tablename__ = "knowledge_graph_nodes"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    node_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Outgoing edges
    outgoing_edges: Mapped[List[KnowledgeGraphEdge]] = relationship(
        "KnowledgeGraphEdge",
        foreign_keys="KnowledgeGraphEdge.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    # Incoming edges
    incoming_edges: Mapped[List[KnowledgeGraphEdge]] = relationship(
        "KnowledgeGraphEdge",
        foreign_keys="KnowledgeGraphEdge.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )


class KnowledgeGraphEdge(Base, UUIDMixin, TimestampMixin):
    """Directed relational edge connecting two Knowledge Graph entities."""
    __tablename__ = "knowledge_graph_edges"

    source_node_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_node_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relation_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    source_node: Mapped[KnowledgeGraphNode] = relationship(
        "KnowledgeGraphNode",
        foreign_keys=[source_node_id],
        back_populates="outgoing_edges",
    )
    target_node: Mapped[KnowledgeGraphNode] = relationship(
        "KnowledgeGraphNode",
        foreign_keys=[target_node_id],
        back_populates="incoming_edges",
    )
