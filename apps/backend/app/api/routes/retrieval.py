"""
FastAPI Routes for the Hybrid Standards Retrieval Engine.

CRITICAL BOUNDARY:
All endpoints return CANDIDATE STANDARDS and RETRIEVAL EVIDENCE.
They do not make legal applicability or final recommendation determinations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db, engine
from app.models.requirement import Requirement, ProcurementSpecification
from app.models.standard import IndianStandard
from app.models.retrieval import RetrievalRun, RetrievalCandidate, StandardIndexEntry, RetrievalRunStatus
from app.schemas.retrieval import (
    RetrievalQueryRequest,
    RetrievalRunRead,
    RetrievalCandidateRead,
    RetrievalEvidenceRead,
    SpecificationRetrievalResult,
    IndexStatusResponse,
    IndexRebuildResponse,
)
from app.services.retrieval.engine import HybridRetrievalEngine
from app.services.retrieval.indexer import INDEX_VERSION, StandardsIndexer

router = APIRouter()
retrieval_engine = HybridRetrievalEngine()


def _serialize_candidate(cand: RetrievalCandidate) -> RetrievalCandidateRead:
    """Helper to transform ORM RetrievalCandidate to Pydantic schema."""
    std = cand.standard
    std_num = std.standard_number if std else f"STD-{cand.standard_id}"
    title = std.title if std else "Unknown Standard"
    status_str = (std.status.value if hasattr(std.status, "value") else str(std.status)) if std else "ACTIVE"
    div_code = std.division_code if std else None
    qco = std.is_mandatory_qco if std else False
    
    ed_year = None
    if cand.edition:
        ed_year = cand.edition.year
    elif std and std.editions:
        ed_year = std.editions[0].year

    evidence_reads = [
        RetrievalEvidenceRead(
            id=ev.id,
            evidence_type=ev.evidence_type,
            snippet=ev.snippet,
            matched_terms=ev.matched_terms or [],
            clause_number=ev.clause_number,
            score=round(ev.score, 4),
        )
        for ev in cand.evidence
    ]

    return RetrievalCandidateRead(
        id=cand.id,
        standard_id=cand.standard_id,
        standard_number=std_num,
        title=title,
        edition_year=ed_year,
        status=status_str,
        division_code=div_code,
        is_mandatory_qco=qco,
        rank=cand.rank,
        lexical_score=round(cand.lexical_score, 4),
        semantic_score=round(cand.semantic_score, 4),
        metadata_score=round(cand.metadata_score, 4),
        rerank_score=round(cand.rerank_score, 4),
        final_retrieval_score=round(cand.final_retrieval_score, 4),
        lexical_rank=cand.lexical_rank,
        semantic_rank=cand.semantic_rank,
        match_reasons=cand.match_reasons or [],
        evidence=evidence_reads,
        provenance_id=std.provenance_id if std else None,
    )


def _serialize_run(run: RetrievalRun) -> RetrievalRunRead:
    """Helper to transform ORM RetrievalRun to Pydantic schema."""
    candidates_read = [_serialize_candidate(c) for c in run.candidates]

    return RetrievalRunRead(
        run_id=run.id,
        specification_id=run.specification_id,
        requirement_id=run.requirement_id,
        query_text=run.query_text,
        query_type=run.query_type,
        top_k=run.top_k,
        status=run.status,
        error_message=run.error_message,
        embedding_model=run.embedding_model,
        embedding_version=run.embedding_version,
        index_version=run.index_version,
        total_candidates_found=run.total_candidates_found,
        execution_duration_ms=run.execution_duration_ms,
        candidates=candidates_read,
        created_at=run.created_at,
    )


# -----------------------------------------------------------------------------
# Retrieval Endpoints
# -----------------------------------------------------------------------------

@router.post("/requirements/{requirement_id}", response_model=RetrievalRunRead, status_code=status.HTTP_200_OK)
def retrieve_candidates_for_requirement(
    requirement_id: int,
    request: RetrievalQueryRequest = RetrievalQueryRequest(),
    db: Session = Depends(get_db),
):
    """
    Retrieve candidate Indian Standards for a specific Requirement.
    Combines lexical BM25, dense semantic search, metadata filtering, and reranking.
    """
    req = db.query(Requirement).filter_by(id=requirement_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {requirement_id} does not exist.",
        )

    try:
        run = retrieval_engine.retrieve_for_requirement(
            db=db,
            requirement=req,
            top_k=request.top_k,
            division_code=request.division_code,
            include_withdrawn=request.include_withdrawn,
            lexical_weight=request.lexical_weight,
            semantic_weight=request.semantic_weight,
        )
        return _serialize_run(run)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval engine failure: {str(e)}",
        )


@router.post("/specifications/{specification_id}", response_model=SpecificationRetrievalResult, status_code=status.HTTP_200_OK)
def retrieve_candidates_for_specification(
    specification_id: int,
    request: RetrievalQueryRequest = RetrievalQueryRequest(),
    db: Session = Depends(get_db),
):
    """
    Batch retrieve candidate Indian Standards across all requirements in a ProcurementSpecification.
    """
    spec = db.query(ProcurementSpecification).filter_by(id=specification_id).first()
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProcurementSpecification with ID {specification_id} does not exist.",
        )

    if not spec.requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Specification {specification_id} contains 0 extracted requirements.",
        )

    runs = retrieval_engine.retrieve_for_specification(
        db=db,
        specification_id=specification_id,
        top_k=request.top_k,
        division_code=request.division_code,
        include_withdrawn=request.include_withdrawn,
    )

    return SpecificationRetrievalResult(
        specification_id=specification_id,
        total_requirements_processed=len(spec.requirements),
        successful_runs=len(runs),
        runs=[_serialize_run(r) for r in runs],
    )


@router.get("/runs/{run_id}", response_model=RetrievalRunRead, status_code=status.HTTP_200_OK)
def get_retrieval_run(run_id: int, db: Session = Depends(get_db)):
    """Retrieve full execution record and candidates of a past retrieval run."""
    run = db.query(RetrievalRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RetrievalRun with ID {run_id} does not exist.",
        )
    return _serialize_run(run)


@router.get("/runs/{run_id}/candidates", response_model=List[RetrievalCandidateRead], status_code=status.HTTP_200_OK)
def get_retrieval_run_candidates(run_id: int, db: Session = Depends(get_db)):
    """Retrieve only the candidate standards identified in a past retrieval run."""
    run = db.query(RetrievalRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RetrievalRun with ID {run_id} does not exist.",
        )
    return [_serialize_candidate(c) for c in run.candidates]


# -----------------------------------------------------------------------------
# Search Index Management Endpoints
# -----------------------------------------------------------------------------

@router.get("/index/status", response_model=IndexStatusResponse, status_code=status.HTTP_200_OK)
def get_index_status(db: Session = Depends(get_db)):
    """Inspect the health, version, and document count of the standards search index."""
    total_indexed = db.query(StandardIndexEntry).count()
    last_entry = db.query(StandardIndexEntry).order_by(StandardIndexEntry.updated_at.desc()).first()
    meta = retrieval_engine.model_metadata
    dialect = "sqlite" if engine.url.drivername.startswith("sqlite") else "postgresql"

    return IndexStatusResponse(
        is_indexed=(total_indexed > 0),
        total_standards_indexed=total_indexed,
        index_version=INDEX_VERSION,
        embedding_model=meta.model_name,
        embedding_dimension=meta.dimension,
        last_indexed_at=last_entry.updated_at if last_entry else None,
        dialect=dialect,
    )


@router.post("/index/rebuild", response_model=IndexRebuildResponse, status_code=status.HTTP_200_OK)
def rebuild_search_index(
    force: bool = Query(default=False, description="Force recomputation of embeddings regardless of content hash"),
    db: Session = Depends(get_db),
):
    """
    Rebuild the search index over all verified Indian Standards in the registry.
    Safe and idempotent.
    """
    total_stds = db.query(IndianStandard).count()
    if total_stds == 0:
        return IndexRebuildResponse(
            success=True,
            standards_indexed=0,
            failures=0,
            index_version=INDEX_VERSION,
            embedding_model=retrieval_engine.model_metadata.model_name,
            duration_ms=0.0,
            message="No verified standards exist in registry to index.",
        )

    indexed, failures, duration_ms = retrieval_engine.indexer.rebuild_index(db=db, force=force)

    return IndexRebuildResponse(
        success=(failures == 0),
        standards_indexed=indexed,
        failures=failures,
        index_version=INDEX_VERSION,
        embedding_model=retrieval_engine.model_metadata.model_name,
        duration_ms=duration_ms,
        message=f"Indexed {indexed} standards with {failures} failures in {duration_ms:.1f}ms.",
    )
