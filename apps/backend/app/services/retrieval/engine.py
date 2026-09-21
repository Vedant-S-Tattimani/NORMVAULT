"""
Master Hybrid Standards Retrieval Engine.
Orchestrates deterministic query construction, lexical BM25, dense semantic search,
metadata filtering, Reciprocal Rank Fusion, feature reranking, and auditable evidence extraction.

CRITICAL BOUNDARY:
This engine discovers CANDIDATE standards. It does not produce final recommendations.
"""

from dataclasses import dataclass
import logging
import time
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from sqlalchemy.orm import Session

from app.models.requirement import Requirement, ProcurementSpecification
from app.models.standard import IndianStandard
from app.models.retrieval import (
    RetrievalRun,
    RetrievalCandidate,
    RetrievalEvidence,
    RetrievalRunStatus,
    EvidenceType,
    StandardIndexEntry,
)
from app.services.retrieval.embeddings import (
    EmbeddingProvider,
    get_embedding_provider,
    EmbeddingVersionMismatchError,
)
from app.services.retrieval.lexical import LexicalSearchEngine
from app.services.retrieval.query_builder import DeterministicQueryBuilder, ConstructedQuery
from app.services.retrieval.metadata_filter import StandardsMetadataFilter, FilterCriteria
from app.services.retrieval.fusion import CandidateFusion, CandidateDraft
from app.services.retrieval.reranker import DeterministicFeatureReranker, RerankerProvider
from app.services.retrieval.indexer import StandardsIndexer, DenseIndexEntry

logger = logging.getLogger(__name__)


@dataclass
class DenseSearchResult:
    standard_id: int
    standard_number: str
    title: str
    semantic_score: float
    scope_text: str
    rank: int


class HybridRetrievalEngine:
    """
    Production Hybrid Retrieval Engine for identifying candidate Indian Standards.
    """

    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        reranker: Optional[RerankerProvider] = None,
        k_rrf: int = 60,
    ):
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.reranker = reranker or DeterministicFeatureReranker()
        self.fusion = CandidateFusion(k_rrf=k_rrf)
        self.indexer = StandardsIndexer(provider=self.embedding_provider)
        self.model_metadata = self.embedding_provider.get_model_metadata()

    def _dense_search(
        self,
        query_vector: List[float],
        dense_entries: List[DenseIndexEntry],
        top_k: int = 20,
    ) -> List[DenseSearchResult]:
        """
        Perform vectorized cosine similarity search over dense index entries.
        Dialect-independent: uses high-speed numpy matrix operations.
        """
        if not dense_entries:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm < 1e-9:
            return []
        q_unit = q_vec / q_norm

        matrix = np.array([e.vector for e in dense_entries], dtype=np.float32)
        # Normalize index vectors
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms < 1e-9] = 1.0
        matrix_unit = matrix / norms

        # Cosine similarities
        similarities = np.dot(matrix_unit, q_unit)

        scored = []
        for idx, sim in enumerate(similarities):
            # Cosine similarity clamped to [0.0, 1.0] for retrieval scoring
            clamped_sim = float(max(0.0, min(1.0, sim)))
            scored.append((clamped_sim, dense_entries[idx]))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for rank, (sim, entry) in enumerate(scored[:top_k], start=1):
            results.append(DenseSearchResult(
                standard_id=entry.standard_id,
                standard_number=entry.standard_number,
                title=entry.title,
                semantic_score=round(sim, 4),
                scope_text=entry.scope,
                rank=rank,
            ))

        return results

    def retrieve_for_requirement(
        self,
        db: Session,
        requirement: Requirement,
        top_k: int = 5,
        division_code: Optional[str] = None,
        include_withdrawn: bool = False,
        lexical_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ) -> RetrievalRun:
        """
        Execute full hybrid retrieval pipeline for a single Requirement.
        """
        t0 = time.time()
        top_k = max(1, min(top_k, 50))  # Enforce safe bounds

        # 1. Inspect Knowledge Base status
        total_standards = db.query(IndianStandard).count()
        if total_standards == 0:
            # Explicit empty knowledge base handling
            run = RetrievalRun(
                requirement_id=requirement.id,
                specification_id=requirement.specification_id,
                query_text=(requirement.extracted_text or "")[:500],
                query_type="SINGLE_REQUIREMENT",
                top_k=top_k,
                status=RetrievalRunStatus.EMPTY_KB,
                error_message="NO_VERIFIED_STANDARDS: The standards registry contains 0 verified standards.",
                embedding_model=self.model_metadata.model_name,
                embedding_version=self.model_metadata.version,
                index_version=self.indexer.metadata.version,
                total_candidates_found=0,
                execution_duration_ms=round((time.time() - t0) * 1000.0, 2),
            )
            db.add(run)
            db.commit()
            return run

        # Auto-ensure index is populated if standards exist but index is empty
        index_count = db.query(StandardIndexEntry).count()
        if index_count == 0:
            self.indexer.rebuild_index(db)

        # 2. Load search indices
        lexical_engine, dense_entries = self.indexer.load_lexical_and_dense_indices(db)

        # 3. Construct deterministic query
        spec = requirement.specification
        product_name = spec.target_product_name if spec else None
        constructed_query: ConstructedQuery = DeterministicQueryBuilder.build_query(
            requirement=requirement,
            target_product_name=product_name,
        )

        query_text = constructed_query.search_text
        if not query_text.strip():
            # Fallback to extracted text
            query_text = requirement.extracted_text or "General Specification"

        # 4. Lexical Search
        lex_pool_size = max(top_k * 3, 20)
        lexical_results = lexical_engine.search(query=query_text, top_k=lex_pool_size)

        # 5. Dense Semantic Search
        q_vector = self.embedding_provider.embed_text(query_text)
        dense_results = self._dense_search(
            query_vector=q_vector,
            dense_entries=dense_entries,
            top_k=lex_pool_size,
        )

        # 6. Candidate Fusion (Reciprocal Rank Fusion)
        fused_candidates: List[CandidateDraft] = self.fusion.fuse(
            lexical_candidates=lexical_results,
            semantic_candidates=dense_results,
            lexical_weight=lexical_weight,
            semantic_weight=semantic_weight,
        )

        # 7. Metadata Filtering & Feature Scoring
        filter_criteria = FilterCriteria(
            division_code=division_code,
            include_withdrawn=include_withdrawn,
        )

        filtered_candidates: List[CandidateDraft] = []
        # Populate standard metadata on drafts
        std_map = {std.id: std for std in db.query(IndianStandard).all()}

        for draft in fused_candidates:
            std = std_map.get(draft.standard_id)
            if not std:
                continue

            draft.edition_year = std.editions[0].year if std.editions else None
            draft.division_code = std.division_code
            draft.is_mandatory_qco = std.is_mandatory_qco
            draft.status = std.status.value if hasattr(std.status, "value") else str(std.status)
            draft.provenance_id = std.provenance_id
            if not draft.scope_text and std.scope:
                draft.scope_text = std.scope

            meta_dict = {
                "status": draft.status,
                "division_code": draft.division_code,
                "is_mandatory_qco": draft.is_mandatory_qco,
                "qco_reference": std.qco_reference,
            }

            passes, meta_score, meta_reasons = StandardsMetadataFilter.evaluate(meta_dict, filter_criteria)
            if passes:
                draft.metadata_score = meta_score
                draft.match_reasons.extend(meta_reasons)
                filtered_candidates.append(draft)

        # 8. Deterministic Cross-Feature Reranking
        reranked_candidates = self.reranker.rerank(
            query=query_text,
            candidates=filtered_candidates,
            explicit_citations=constructed_query.explicit_standard_numbers,
        )

        # 9. Top-K Slicing & Evidence Synthesis
        final_drafts = reranked_candidates[:top_k]

        duration_ms = round((time.time() - t0) * 1000.0, 2)

        # 10. Persist Traceable Retrieval Run
        run = RetrievalRun(
            specification_id=requirement.specification_id,
            requirement_id=requirement.id,
            query_text=query_text,
            query_type="SINGLE_REQUIREMENT",
            top_k=top_k,
            status=RetrievalRunStatus.COMPLETED,
            embedding_model=self.model_metadata.model_name,
            embedding_version=self.model_metadata.version,
            index_version=self.indexer.metadata.version,
            lexical_weight=lexical_weight,
            semantic_weight=semantic_weight,
            total_candidates_found=len(reranked_candidates),
            execution_duration_ms=duration_ms,
        )
        db.add(run)
        db.flush()

        # Build candidate and evidence models
        for rank, draft in enumerate(final_drafts, start=1):
            db_cand = RetrievalCandidate(
                run_id=run.id,
                standard_id=draft.standard_id,
                edition_id=draft.edition_id,
                rank=rank,
                lexical_score=draft.lexical_score,
                semantic_score=draft.semantic_score,
                metadata_score=draft.metadata_score,
                rerank_score=draft.rerank_score,
                final_retrieval_score=draft.final_retrieval_score,
                lexical_rank=draft.lexical_rank,
                semantic_rank=draft.semantic_rank,
                match_reasons=draft.match_reasons,
            )
            db.add(db_cand)
            db.flush()

            # Real Retrieval Evidence items:
            # 1. Lexical match evidence
            if draft.matched_tokens:
                ev_lex = RetrievalEvidence(
                    candidate_id=db_cand.id,
                    evidence_type=EvidenceType.LEXICAL_MATCH,
                    snippet=f"Lexical BM25 matched terms: {', '.join(draft.matched_tokens)}",
                    matched_terms=draft.matched_tokens,
                    score=draft.lexical_score,
                )
                db.add(ev_lex)

            # 2. Semantic match evidence
            if draft.semantic_score > 0:
                ev_sem = RetrievalEvidence(
                    candidate_id=db_cand.id,
                    evidence_type=EvidenceType.SEMANTIC_SIMILARITY,
                    snippet=f"Semantic dense cosine similarity score: {draft.semantic_score:.4f}",
                    score=draft.semantic_score,
                )
                db.add(ev_sem)

            # 3. Scope overlap evidence
            if draft.scope_text:
                scope_snippet = draft.scope_text[:280] + ("..." if len(draft.scope_text) > 280 else "")
                ev_scope = RetrievalEvidence(
                    candidate_id=db_cand.id,
                    evidence_type=EvidenceType.SCOPE_OVERLAP,
                    snippet=f"Scope Excerpt: {scope_snippet}",
                    score=draft.rerank_score,
                )
                db.add(ev_scope)

            # 4. Metadata match evidence
            if draft.match_reasons:
                ev_meta = RetrievalEvidence(
                    candidate_id=db_cand.id,
                    evidence_type=EvidenceType.METADATA_MATCH,
                    snippet="; ".join(draft.match_reasons),
                    score=draft.metadata_score,
                )
                db.add(ev_meta)

        db.commit()
        db.refresh(run)
        return run

    def retrieve_for_specification(
        self,
        db: Session,
        specification_id: int,
        top_k: int = 5,
        division_code: Optional[str] = None,
        include_withdrawn: bool = False,
    ) -> List[RetrievalRun]:
        """
        Execute candidate retrieval across all requirements in a ProcurementSpecification.
        Maintains individual requirement linkage for downstream Phase 4 synthesis.
        """
        spec = db.query(ProcurementSpecification).filter_by(id=specification_id).first()
        if not spec:
            raise ValueError(f"Specification with id {specification_id} not found.")

        runs: List[RetrievalRun] = []
        for req in spec.requirements:
            run = self.retrieve_for_requirement(
                db=db,
                requirement=req,
                top_k=top_k,
                division_code=division_code,
                include_withdrawn=include_withdrawn,
            )
            runs.append(run)

        return runs
