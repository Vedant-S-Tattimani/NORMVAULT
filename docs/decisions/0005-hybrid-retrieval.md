# Architectural Decision Record 0005: Hybrid Standards Retrieval Engine

## Status
Accepted

## Date
2026-09-20

## Context
In NORMVAULT (SIH Problem Statement 26108), the system must map unstructured and structured procurement specifications to relevant Indian Standards (IS). Pure lexical keyword matching fails on synonymy and semantic paraphrasing (e.g. "polyethylene pipe for potable water" vs "conveyance of drinking water"). Pure dense vector search fails on precise alphanumeric citations (e.g. "IS 12615:2018" vs "IS 12615:2011", or "Grade E250"). Furthermore, calling an LLM directly as an end-to-end retriever over 20,000+ standards is computationally prohibitive, non-deterministic, and prone to hallucinations.

## Decision
We implemented a **Hybrid Standards Retrieval Engine** combining:
1. **Deterministic Query Construction**: Extracts product identities, parameters, and explicit BIS citations without arbitrary prompt alteration.
2. **Lexical Retrieval (BM25Okapi)**: Provides exact token and standard number matching with field-level boosts.
3. **Dense Semantic Retrieval**: Vector cosine similarity over canonical structured standards document representations with versioned embeddings.
4. **Reciprocal Rank Fusion (RRF)**: Merges rank streams with standard smoothing ($k=60$) to prevent scale distortions between unbounded BM25 and bounded cosine scores.
5. **Deterministic Feature Reranker**: Refines candidates using domain interaction features (explicit citations, title Jaccard, scope coverage).
6. **Isolated Retrieval Scores**: Component scores (`lexical_score`, `semantic_score`, `metadata_score`, `rerank_score`, `final_retrieval_score`) remain visible and uncorrupted.
7. **Strict Boundary**: Phase 3 outputs `CANDIDATE STANDARDS` and `RETRIEVAL EVIDENCE`. It explicitly avoids deciding final recommendations or legal compliance (Phase 4).

## Consequences
- **Positive**: High precision on exact standard number searches while maintaining high recall on conceptual paraphrases.
- **Positive**: 100% reproducible and testable in local development and air-gapped CI environments.
- **Positive**: Dialect independence (NumPy cosine similarity in SQLite, pgvector in PostgreSQL).
- **Positive**: No hallucinated standards or ambiguous "AI confidence" percentages.
- **Negative**: Requires maintaining an indexing layer and reindexing when standards metadata or embedding models change.
