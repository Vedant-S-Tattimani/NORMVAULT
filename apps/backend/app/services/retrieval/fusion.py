"""
Candidate Fusion layer combining lexical and dense semantic retrieval streams.
Uses Reciprocal Rank Fusion (RRF) with component score preservation for complete auditable transparency.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class CandidateDraft:
    """A working candidate standard passing through the retrieval pipeline."""
    standard_id: int
    standard_number: str
    title: str
    edition_id: Optional[int] = None
    edition_year: Optional[int] = None
    status: str = "ACTIVE"
    division_code: Optional[str] = None
    is_mandatory_qco: bool = False
    
    # Ranks in individual systems
    lexical_rank: Optional[int] = None
    semantic_rank: Optional[int] = None
    
    # Granular component scores
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    metadata_score: float = 0.0
    rerank_score: float = 0.0
    rrf_score: float = 0.0
    final_retrieval_score: float = 0.0

    # Evidence and match explanations
    matched_tokens: List[str] = field(default_factory=list)
    match_reasons: List[str] = field(default_factory=list)
    scope_text: str = ""
    clauses_text: str = ""
    provenance_id: Optional[int] = None


class CandidateFusion:
    """
    Combines lexical BM25 rankings and dense semantic vector rankings using
    Reciprocal Rank Fusion (RRF; Cormack et al., 2009).
    
    RRF is rank-based rather than score-scale dependent, preventing lexical scores
    (which are unbounded) from skewing dense cosine similarity scores.
    """

    def __init__(self, k_rrf: int = 60):
        self.k_rrf = k_rrf

    def fuse(
        self,
        lexical_candidates: List[Any],
        semantic_candidates: List[Any],
        lexical_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ) -> List[CandidateDraft]:
        """
        Merge candidate lists into a deduplicated candidate pool with RRF scores.
        """
        # standard_id -> CandidateDraft
        pool: Dict[int, CandidateDraft] = {}

        # 1. Process Lexical Candidates
        for rank, cand in enumerate(lexical_candidates, start=1):
            sid = cand.standard_id
            if sid not in pool:
                pool[sid] = CandidateDraft(
                    standard_id=sid,
                    standard_number=cand.standard_number,
                    title=cand.title,
                    lexical_rank=rank,
                    lexical_score=cand.normalized_score,
                    matched_tokens=list(getattr(cand, "matched_tokens", [])),
                )
            else:
                pool[sid].lexical_rank = rank
                pool[sid].lexical_score = cand.normalized_score
                pool[sid].matched_tokens = list(getattr(cand, "matched_tokens", []))

        # 2. Process Semantic Candidates
        for rank, cand in enumerate(semantic_candidates, start=1):
            sid = cand.standard_id
            if sid not in pool:
                pool[sid] = CandidateDraft(
                    standard_id=sid,
                    standard_number=cand.standard_number,
                    title=cand.title,
                    semantic_rank=rank,
                    semantic_score=cand.semantic_score,
                    scope_text=getattr(cand, "scope_text", ""),
                )
            else:
                pool[sid].semantic_rank = rank
                pool[sid].semantic_score = cand.semantic_score
                if hasattr(cand, "scope_text") and cand.scope_text:
                    pool[sid].scope_text = cand.scope_text

        # 3. Compute RRF Score for each candidate
        # Formula: w_lex / (k + R_lex) + w_sem / (k + R_sem)
        raw_rrf_scores: Dict[int, float] = {}
        for sid, draft in pool.items():
            rrf_val = 0.0
            if draft.lexical_rank is not None:
                rrf_val += lexical_weight * (1.0 / (self.k_rrf + draft.lexical_rank))
            if draft.semantic_rank is not None:
                rrf_val += semantic_weight * (1.0 / (self.k_rrf + draft.semantic_rank))
            raw_rrf_scores[sid] = rrf_val

        # Normalize RRF scores to [0.0, 1.0]
        max_rrf = max(raw_rrf_scores.values()) if raw_rrf_scores else 1.0

        for sid, draft in pool.items():
            normalized_rrf = raw_rrf_scores[sid] / max_rrf if max_rrf > 0 else 0.0
            draft.rrf_score = round(normalized_rrf, 4)
            # Intermediate retrieval score combines RRF with component scores
            draft.final_retrieval_score = draft.rrf_score

        # Return sorted by RRF score descending
        sorted_candidates = sorted(pool.values(), key=lambda c: c.rrf_score, reverse=True)
        return sorted_candidates
