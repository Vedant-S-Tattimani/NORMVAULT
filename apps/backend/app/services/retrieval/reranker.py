"""
Reranking abstraction and deterministic cross-feature reranker.
Computes fine-grained feature interactions (citation matching, title overlap, scope relevance)
without opaque LLM halluncinations.
"""

from abc import ABC, abstractmethod
import re
from typing import List, Optional, Set
from app.services.retrieval.fusion import CandidateDraft


def _clean_tokens(text: str) -> Set[str]:
    """Tokenize text into lowercase alphanumeric set for set-theoretic comparison."""
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return {t for t in cleaned.split() if len(t) > 2}


class RerankerProvider(ABC):
    """Abstract interface for candidate rerankers."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: List[CandidateDraft],
        explicit_citations: Optional[List[str]] = None,
    ) -> List[CandidateDraft]:
        """Rerank candidate drafts and update component scores."""
        pass


class DeterministicFeatureReranker(RerankerProvider):
    """
    Deterministic cross-feature reranker.
    Evaluates:
    - Explicit BIS standard citations in query (e.g. 'IS 12615' in tender)
    - Jaccard similarity between query tokens and standard title
    - Scope coverage of query key concepts
    - Lexical + Semantic harmonic balance
    - Statutory QCO compliance signals
    """

    def rerank(
        self,
        query: str,
        candidates: List[CandidateDraft],
        explicit_citations: Optional[List[str]] = None,
    ) -> List[CandidateDraft]:
        if not candidates:
            return []

        query_tokens = _clean_tokens(query)
        citations_set = set(explicit_citations or [])

        for cand in candidates:
            cand_number_clean = cand.standard_number.upper().replace(":", " ").replace("-", " ")
            cand_title_tokens = _clean_tokens(cand.title)
            cand_scope_tokens = _clean_tokens(cand.scope_text)

            # 1. Explicit citation match
            is_explicitly_cited = False
            for cite in citations_set:
                cite_clean = cite.upper().replace(":", " ").replace("-", " ")
                if cite_clean in cand_number_clean or cand_number_clean in cite_clean:
                    is_explicitly_cited = True
                    break

            if not is_explicitly_cited:
                # Also check direct occurrence of standard number digits in query
                std_digits = re.findall(r"\b\d{2,6}\b", cand.standard_number)
                for dig in std_digits:
                    if dig in query:
                        is_explicitly_cited = True
                        break

            citation_boost = 1.0 if is_explicitly_cited else 0.0
            if is_explicitly_cited:
                cand.match_reasons.append(f"Explicit reference to {cand.standard_number} detected in specification text")

            # 2. Title Token Jaccard Overlap
            title_overlap = len(query_tokens & cand_title_tokens)
            title_union = len(query_tokens | cand_title_tokens)
            title_jaccard = (title_overlap / title_union) if title_union > 0 else 0.0
            if title_overlap > 0:
                matched_title_terms = list(query_tokens & cand_title_tokens)
                cand.match_reasons.append(f"Title matches key terms: {', '.join(sorted(matched_title_terms)[:4])}")

            # 3. Scope Keyword Density
            scope_overlap = len(query_tokens & cand_scope_tokens)
            scope_score = min(scope_overlap / max(len(query_tokens), 1), 1.0)
            if scope_overlap > 1:
                cand.match_reasons.append(f"Candidate scope covers {scope_overlap} requirement concepts")

            # 4. Multi-channel Agreement (reward candidates found by both lexical and dense)
            both_channels = 1.0 if (cand.lexical_score > 0.1 and cand.semantic_score > 0.3) else 0.0
            if both_channels > 0:
                cand.match_reasons.append("High cross-channel agreement (both lexical and dense matches)")

            # Compute Weighted Rerank Score [0.0 to 1.0]
            if is_explicitly_cited:
                # Direct citation has paramount relevance for retrieval candidate pool
                raw_rerank = 0.50 + 0.20 * title_jaccard + 0.15 * scope_score + 0.15 * cand.metadata_score
            else:
                raw_rerank = (
                    0.30 * title_jaccard +
                    0.25 * scope_score +
                    0.20 * cand.semantic_score +
                    0.15 * cand.lexical_score +
                    0.10 * cand.metadata_score
                )

            cand.rerank_score = round(min(max(raw_rerank, 0.0), 1.0), 4)

            # Final Retrieval Score: Weighted blend of fused RRF rank score and rerank score
            fused = 0.45 * cand.rrf_score + 0.55 * cand.rerank_score
            cand.final_retrieval_score = round(min(max(fused, 0.0), 1.0), 4)

        # Sort descending by final retrieval score
        candidates.sort(key=lambda c: c.final_retrieval_score, reverse=True)
        return candidates
