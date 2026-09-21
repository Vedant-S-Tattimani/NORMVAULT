"""
Pydantic v2 Schemas for the Hybrid Standards Retrieval Engine.

CRITICAL TERMINOLOGY BOUNDARY:
Schemas represent candidate retrieval and discovery results.
Never label results as 'recommendations', 'compliances', or 'decisions'.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.retrieval import RetrievalRunStatus, EvidenceType


class RetrievalQueryRequest(BaseModel):
    """Configuration options for a requirement retrieval query."""
    top_k: int = Field(default=5, ge=1, le=50, description="Configurable candidate count limit (1 to 50)")
    division_code: Optional[str] = Field(default=None, description="Optional filter by BIS technical division (e.g. ETD, CED)")
    include_withdrawn: bool = Field(default=False, description="Whether to include superseded/withdrawn standards")
    lexical_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight for lexical retrieval in candidate fusion")
    semantic_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight for semantic retrieval in candidate fusion")


class RetrievalEvidenceRead(BaseModel):
    """Auditable evidence backing why a standard candidate was retrieved."""
    id: Optional[int] = None
    evidence_type: EvidenceType
    snippet: str
    matched_terms: Optional[List[str]] = None
    clause_number: Optional[str] = None
    score: float = Field(default=0.0, description="Component relevance score for this specific evidence slice")

    model_config = ConfigDict(from_attributes=True)


class RetrievalCandidateRead(BaseModel):
    """A candidate Indian Standard surfaced by the hybrid retrieval engine."""
    id: Optional[int] = None
    standard_id: int
    standard_number: str
    title: str
    edition_year: Optional[int] = None
    status: str
    division_code: Optional[str] = None
    is_mandatory_qco: bool = False
    rank: int = Field(description="1-based retrieval ranking in this run")
    
    # Granular component scores (0.0 to 1.0)
    lexical_score: float = Field(description="Normalized BM25 lexical keyword relevance score")
    semantic_score: float = Field(description="Cosine similarity from dense semantic embedding")
    metadata_score: float = Field(description="Metadata relevance boost (e.g. status, QCO, division match)")
    rerank_score: float = Field(description="Cross-feature reranking score")
    final_retrieval_score: float = Field(description="Overall candidate fusion retrieval score")

    # Intermediate rank positions
    lexical_rank: Optional[int] = None
    semantic_rank: Optional[int] = None
    match_reasons: Optional[List[str]] = None
    
    # Traceable evidence
    evidence: List[RetrievalEvidenceRead] = Field(default_factory=list)
    provenance_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class RetrievalRunRead(BaseModel):
    """Full execution summary of a standards retrieval run."""
    run_id: int
    specification_id: Optional[int] = None
    requirement_id: Optional[int] = None
    query_text: str
    query_type: str
    top_k: int
    status: RetrievalRunStatus
    error_message: Optional[str] = None
    
    # Engine & algorithm metadata
    embedding_model: str
    embedding_version: str
    index_version: str
    total_candidates_found: int
    execution_duration_ms: float
    
    candidates: List[RetrievalCandidateRead] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SpecificationRetrievalResult(BaseModel):
    """Aggregated candidate discovery results for all requirements in a specification."""
    specification_id: int
    total_requirements_processed: int
    successful_runs: int
    runs: List[RetrievalRunRead] = Field(default_factory=list)


class IndexStatusResponse(BaseModel):
    """Health and version metadata of the standards search index."""
    is_indexed: bool
    total_standards_indexed: int
    index_version: str
    embedding_model: str
    embedding_dimension: int
    last_indexed_at: Optional[datetime] = None
    dialect: str = Field(description="Underlying database dialect (sqlite or postgresql)")


class IndexRebuildResponse(BaseModel):
    """Result of an index rebuild operation."""
    success: bool
    standards_indexed: int
    failures: int
    index_version: str
    embedding_model: str
    duration_ms: float
    message: str
