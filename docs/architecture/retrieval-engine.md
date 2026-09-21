# Architecture: Hybrid Standards Retrieval Engine (Phase 3)

## 1. Executive Summary

The **Hybrid Standards Retrieval Engine** is Phase 3 of NORMVAULT (SIH Problem Statement 26108). Its objective is to take structured procurement requirements and technical parameters from Phase 2 and discover plausible candidate Indian Standards from the verified Standards Knowledge Foundation established in Phase 1.

```
Requirement (+ Technical Parameters)
           │
           ▼
 Deterministic Query Constructor
           │
     ┌─────┴────────────────┐
     ▼                      ▼
Lexical Search (BM25)  Dense Search (EmbeddingProvider)
     │                      │
     └──────┬───────────────┘
            ▼
   Candidate Pool & Union
            │
            ▼
    Metadata Filtering (Status, Division, QCO)
            │
            ▼
 Candidate Fusion (Reciprocal Rank Fusion + Component Scoring)
            │
            ▼
 Reranker (Deterministic Cross-Feature / Cross-Encoder)
            │
            ▼
    Candidate Standards + Retrieval Evidence
```

---

## 2. Critical Boundary: Candidates vs. Recommendations

> [!IMPORTANT]
> **Strict Semantic Boundary**:
> Phase 3 answers: *"Which standards are plausible candidates for this requirement and why were they retrieved?"*
> Phase 3 does **not** decide: *"This is definitely the applicable standard"* or *"This specification is compliant."*
> All outputs are explicitly classified as `RETRIEVAL CANDIDATE` records. Scores represent multi-channel retrieval relevance signals, not legal adoption probabilities.

---

## 3. Retrieval Pipeline Stages

### Stage 1: Deterministic Query Construction
Transforms incoming `Requirement` and `TechnicalParameter` records into a clean, normalized query representation.
- Extracts target product identity (e.g. `"Three Phase Induction Motor"`)
- Extracts clause text (e.g. `"Rated power shall be 15 kW with efficiency class IE3"`)
- Extracts normalized technical parameters (e.g. `"power 15 kW", "poles 4", "efficiency IE3"`)
- Detects explicit standard citations via regex `IS\s*[:\-]?\s*(\d{2,6})`

### Stage 2: Dual Retrieval Channels
- **Lexical Search (BM25Okapi)**:
  - Inverted index with Robertson-Spärck Jones IDF and BM25 term weighting ($k_1 = 1.5, b = 0.75$).
  - Field-level boosting: standard number (4x), title (3x), scope (1x), key clauses (1x).
  - Extracts exact matched tokens for evidence tracking.
- **Dense Semantic Retrieval (EmbeddingProvider)**:
  - Vector cosine similarity over canonical structured standards document embeddings.
  - Generates dense semantic scores bounded in $[0.0, 1.0]$.
  - Supported providers: `DeterministicMockEmbeddingProvider` (offline/CI) and `SentenceTransformerEmbeddingProvider` (neural).

### Stage 3: Metadata Filtering
Evaluates candidates against structured domain constraints:
- Excludes withdrawn/superseded standards unless explicitly requested via `include_withdrawn = True`.
- Filters by BIS technical division (e.g. `ETD`, `CED`, `MTD`) when specified.
- Applies statutory Quality Control Order (QCO) boosting (+0.20 score) for mandatory BIS certification standards.

### Stage 4: Candidate Fusion (Reciprocal Rank Fusion)
Combines heterogeneous rankers without arbitrary score scaling issues using Reciprocal Rank Fusion:
$$RRF(d) = \frac{w_{lex}}{60 + R_{lex}(d)} + \frac{w_{sem}}{60 + R_{sem}(d)}$$
Maintains isolated component scores:
- `lexical_score`: Normalized BM25 score relative to max
- `semantic_score`: Dense cosine similarity
- `metadata_score`: Status and QCO boost score
- `rrf_score`: Normalized fused rank score

### Stage 5: Deterministic Cross-Feature Reranker
Evaluates fine-grained cross-channel interactions:
- Exact standard number reference bonus (+0.35 boost if tender cites standard)
- Jaccard title token overlap
- Scope requirement concept coverage
- Lexical + Semantic harmonic balance

### Stage 6: Traceable Retrieval Evidence
Every candidate standard includes verified evidence items:
- `LEXICAL_MATCH`: Specific tokens matched in query and document
- `SEMANTIC_SIMILARITY`: Cosine similarity score of dense vector representations
- `SCOPE_OVERLAP`: Textual excerpts from the candidate standard's official scope
- `METADATA_MATCH`: Verification of active status, gazetted amendments, or QCO mandate

---

## 4. Search Index Storage & Dual Dialect Strategy

Standards index entries (`standard_index_entries`) store:
- `standard_id`, `edition_id`
- `index_version` (e.g. `v1.0`)
- `embedding_model` and `embedding_dimension`
- `content_hash` (SHA-256)
- `indexed_text` (canonical standard document)
- `embedding_vector` (JSON serialized float array / vector)

**Dialect Independence**:
- SQLite (Local Dev & Unit Tests): High-speed matrix cosine similarity in NumPy.
- PostgreSQL (Production / Staging): Native `pgvector` operators (`<=>`, `<#>`).
