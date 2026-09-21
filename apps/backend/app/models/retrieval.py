"""
Domain models for the Hybrid Standards Retrieval Engine.
Tracks retrieval runs, candidates, multi-component scores, and traceable evidence.

CRITICAL BOUNDARY:
Retrieval models represent candidate discovery and search relevance, NOT final recommendations
or legal applicability determinations (which belong to Phase 4).
"""

from enum import Enum
from typing import List, Optional, Any, Dict
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, Float, ForeignKey, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class RetrievalRunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EMPTY_KB = "EMPTY_KB"


class EvidenceType(str, Enum):
    LEXICAL_MATCH = "LEXICAL_MATCH"
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
    SCOPE_OVERLAP = "SCOPE_OVERLAP"
    CLAUSE_MATCH = "CLAUSE_MATCH"
    METADATA_MATCH = "METADATA_MATCH"


class StandardIndexEntry(Base, TimestampMixin):
    """
    Persisted searchable representation of a verified Indian Standard.
    Stores canonical indexed text, embedding vector, content hash, and model metadata.
    """
    __tablename__ = "standard_index_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    standard_id: Mapped[int] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    index_version: Mapped[str] = mapped_column(String(32), default="v1.0", nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    indexed_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Stored as JSON list of floats for dialect independence (SQLite & PostgreSQL).
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    metadata_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    standard: Mapped["IndianStandard"] = relationship("IndianStandard")
    edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition")


class RetrievalRun(Base, TimestampMixin):
    """
    Traceable execution record of a standards retrieval operation.
    Captures query input, active index metadata, parameters, and execution state.
    """
    __tablename__ = "retrieval_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specification_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("procurement_specifications.id", ondelete="CASCADE"), nullable=True, index=True
    )
    requirement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("spec_requirements.id", ondelete="CASCADE"), nullable=True, index=True
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(64), default="SINGLE_REQUIREMENT", nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    status: Mapped[RetrievalRunStatus] = mapped_column(
        SQLEnum(RetrievalRunStatus), default=RetrievalRunStatus.COMPLETED, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Engine & algorithm metadata for reproducibility
    embedding_model: Mapped[str] = mapped_column(String(128), default="mock-deterministic", nullable=False)
    embedding_version: Mapped[str] = mapped_column(String(32), default="v1.0", nullable=False)
    index_version: Mapped[str] = mapped_column(String(32), default="v1.0", nullable=False)
    lexical_weight: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    semantic_weight: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    total_candidates_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    candidates: Mapped[List["RetrievalCandidate"]] = relationship(
        "RetrievalCandidate", back_populates="run", cascade="all, delete-orphan", order_by="RetrievalCandidate.rank"
    )
    requirement: Mapped[Optional["Requirement"]] = relationship("Requirement")
    specification: Mapped[Optional["ProcurementSpecification"]] = relationship("ProcurementSpecification")


class RetrievalCandidate(Base, TimestampMixin):
    """
    A candidate Indian Standard identified by the retrieval engine.
    Retains isolated component scores for complete auditable transparency.
    """
    __tablename__ = "retrieval_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("retrieval_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    standard_id: Mapped[int] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    # Component scores (explicitly separated, never collapsed into an opaque "confidence")
    lexical_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    semantic_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metadata_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rerank_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    final_retrieval_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Intermediate rank positions prior to fusion
    lexical_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    semantic_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    match_reasons: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Relationships
    run: Mapped["RetrievalRun"] = relationship("RetrievalRun", back_populates="candidates")
    standard: Mapped["IndianStandard"] = relationship("IndianStandard")
    edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition")
    evidence: Mapped[List["RetrievalEvidence"]] = relationship(
        "RetrievalEvidence", back_populates="candidate", cascade="all, delete-orphan"
    )


class RetrievalEvidence(Base, TimestampMixin):
    """
    Concrete evidence backing why a candidate was retrieved.
    Derives from actual matched lexical tokens, semantic similarity metrics,
    scope excerpts, or clause correlations.
    """
    __tablename__ = "retrieval_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("retrieval_candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        SQLEnum(EvidenceType), default=EvidenceType.LEXICAL_MATCH, nullable=False
    )
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    matched_terms: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    clause_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_clauses.id", ondelete="SET NULL"), nullable=True
    )
    clause_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    candidate: Mapped["RetrievalCandidate"] = relationship("RetrievalCandidate", back_populates="evidence")
    clause: Mapped[Optional["Clause"]] = relationship("Clause")
