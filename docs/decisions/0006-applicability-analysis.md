# 0006. Applicability Analysis & Standards Recommendation Engine

Date: 2026-09-21  
Status: Accepted  
Deciders: NORMVAULT Engineering Core  

## Context

Phase 3 produced Candidate Standards ranked by multi-channel retrieval scores (BM25 + Dense Semantic Embeddings + Reciprocal Rank Fusion). However, semantic similarity does not equal legal or technical applicability. Recommending a standard solely because it shares keywords or concepts with a tender leads to false positives (e.g., recommending a domestic appliance standard for an industrial pump or recommending a standard whose voltage bounds exclude the specified voltage).

Furthermore, procurement officers require transparent, evidence-first justifications: which clauses apply, what parameters were checked, whether any scope exclusions exist, and what critical information is missing from the tender.

## Decision

1. **Explicit Multi-State Decision Outcomes**:
   Adopt four explicit states: `APPLICABLE`, `POSSIBLY_APPLICABLE`, `NOT_APPLICABLE`, and `INSUFFICIENT_EVIDENCE`. Reject binary classification and mandate principled abstention.

2. **Component Evidence Matrix (No Uncalibrated Percentages)**:
   Expose multi-criteria evidence components (`scope_match`, `product_match`, `parameter_match`, `application_match`, `explicit_reference`, `exclusion_match`, `negative_evidence`). Avoid misleading "AI confidence = 94%" metrics. The `evidence_alignment_index` is formally defined as a multi-criteria evidence alignment measure.

3. **Strict Priority for Negative Evidence**:
   Any verified fatal conflict (domain mismatch, operating environment conflict, out-of-range technical parameter, or explicit exclusion clause) strictly overrides high retrieval scores, forcing the candidate to `NOT_APPLICABLE`.

4. **Multi-Candidate Resolution & Abstention on Ties**:
   When multiple candidates are plausible, prioritize standards with specific sub-feature alignment (e.g. `IE3`). If two standards remain tied without distinguishing data, designate both as `MULTIPLE_PLAUSIBLE_STANDARDS` and explain what information is missing.

5. **Grounded Synthesis & Defense-in-Depth**:
   Procurement documents are treated as untrusted data. Generated references are verified against the active BIS standards database before serialization, ensuring zero fabricated standards, clauses, or parameters.

## Consequences

- **Positive**: Zero false-positive recommendations on out-of-scope standards; full auditability and clause-level traceability for every procurement decision; resilient against prompt injection attacks.
- **Negative**: The engine will deliberately abstain (`INSUFFICIENT_EVIDENCE`) when tenders omit essential engineering parameters, requiring user clarification.
