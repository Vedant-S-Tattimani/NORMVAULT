# Embedding Strategy & Index Content Construction

## 1. Overview

The dense semantic retrieval stream of NORMVAULT relies on reproducible, versioned vector embeddings computed over canonical document representations of verified Indian Standards.

---

## 2. Canonical Content Construction Hierarchy

To prevent arbitrary or noisy embedding representations, each Indian Standard is serialized into a structured canonical document:

```text
Standard Number: {standard_number}
Title: {title}
Status: {status}
Division: {division_code}
Department: {department}
Mandatory Quality Control Order (QCO): YES (Ref: {qco_reference})
Scope: {scope}
Current Edition: Year {year} (Edition {edition_number})
Key Clauses:
- Clause {clause_number}: {content}
Normative References:
- Ref: {target_standard_number} ({relationship_type})
```

### Hierarchy Rules:
1. **Standard Identity First**: Standard number, full legal title, division, and status form the initial grounding tokens.
2. **Statutory Status**: If covered by a mandatory QCO gazette, this is explicitly declared to steer semantic representations towards statutory compliance contexts.
3. **Official Scope**: The full verified scope from BIS gazettes is included intact.
4. **Key Clauses**: Up to 15 key technical clauses from the current edition are incorporated to capture domain terminology (e.g. pressure ratings, test methods, tolerances).
5. **Normative References**: Explicit cross-citations are included to anchor related standards in vector space.

---

## 3. Content Hashing & Change Detection

Every indexed standard has a SHA-256 `content_hash` computed over its canonical document text:
$$\text{content\_hash} = \text{SHA-256}(\text{canonical\_standard\_text})$$

When `rebuild_index()` is invoked:
1. If an index entry exists and `content_hash`, `embedding_model`, and `embedding_dimension` match: the standard is skipped (incremental indexing).
2. If the standard's scope, clauses, or metadata have changed, the hash differs, triggering vector re-embedding.
3. If `force=True` is provided, all vectors are recomputed unconditionally.

---

## 4. Embedding Model Versioning & Safety Guards

Silent vector corruption occurs when queries embedded with Model B are matched against index vectors generated with Model A. NORMVAULT enforces strict version consistency:

```
Query Embedding Request
          │
          ▼
   Model & Dimension Check
          │
   ┌──────┴──────────────────────────┐
   ▼                                 ▼
Matches Index Model?             Mismatch Detected!
   │                                 │
   ▼                                 ▼
Execute Vector Search         Raise EmbeddingVersionMismatchError
                              ("Index rebuilt with model X, active is Y")
```

Every `StandardIndexEntry` persists:
- `embedding_model`: String identifier (e.g. `mock-deterministic-128d` or `all-MiniLM-L6-v2`)
- `embedding_dimension`: Integer dimension (e.g. 128 or 384)
- `index_version`: Version string (e.g. `v1.0`)

If a query provider does not match the stored index metadata, the engine refuses execution and instructs the administrator to trigger `POST /api/v1/retrieval/index/rebuild`.

---

## 5. Providers

### 1. `DeterministicMockEmbeddingProvider` (Default Dev & Testing)
- Pure Python and NumPy implementation.
- Generates reproducible, unit-normalized vectors via token hashing and n-gram projections.
- No network requests, zero cold-start delay, 100% deterministic for CI pipelines.

### 2. `SentenceTransformerEmbeddingProvider` (Neural Production)
- Uses local `sentence-transformers` models (e.g. `all-MiniLM-L6-v2` or multilingual Indian models).
- 384-dimensional dense vectors with cosine similarity.
