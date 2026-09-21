# Architectural Decision Record (ADR) 0008: Standard Edition, Amendment & Currentness Intelligence

## Status
**ACCEPTED** (2026-09-21)

## Context
In public procurement and technical compliance evaluation (SIH PS 26108), standards citations pose significant challenges:
1. Public tenders regularly cite historical standards (e.g., `IS 325:1996`) that have been superseded by newer standards (`IS 12615:2018`).
2. Standards undergo incremental amendments that alter normative tolerances without creating a new edition.
3. Procurement text often cites a standard without specifying an edition (`IS 12615`), or contains conflicting citations across clauses.
4. Many automated AI tools blindly assume that the newest published standard is the applicable standard, which leads to legal disqualifications and procurement audit failures.
5. In other cases, AI models hallucinate amendments, supersession dates, or clause diffs when data is missing.

## Decision
We established the following architectural decisions for Phase 6:

1. **Standard Family vs. Edition Decoupling**:
   `IndianStandard` represents the persistent conceptual family (e.g. `IS 12615`). `StandardEdition` represents an immutable publication year (e.g. 2018). All amendments are attached strictly to their parent `StandardEdition`.

2. **Strict Multi-Tier Precedence Rule**:
   Precedence order:
   (1) Explicit tender citations (with contradiction detection).
   (2) QCO statutory edition mandates.
   (3) Database-verified edition status and supersession/withdrawal provenance.
   (4) Active amendment chain assembly.
   (5) Principled abstention (`CURRENTNESS_UNCERTAIN`) if records are incomplete.

3. **Never Assume Newest = Applicable**:
   If a tender cites `IS 325:1996`, NORMVAULT preserves `IS 325:1996` as the evaluated entity, marks it as `SUPERSEDED`, and emits a clear procurement warning indicating that a newer edition exists (`IS 12615:2018`). The system never silently substitutes the standard or edition.

4. **Zero Fabrication Policy for Amendments**:
   When an amendment affects a clause, old and new clause text are displayed only if verified verbatim in the database. If not indexed, the system emits `"Amendment identified; clause impact not indexed."`

5. **Prompt Injection Immunity**:
   Procurement specification content is strictly untrusted data. No system instructions embedded in tender text can override database status.

6. **Edition-Scoped Dependency Graph**:
   Normative references and QCO mandates are version-scoped. References belonging to `IS 12615:2018` do not leak into `IS 12615:2011` or other editions.

## Consequences

### Positive
- Contractual fidelity is preserved: procurement officers see exactly what the tender cited alongside statutory facts.
- Audit safety: QCO compliance failures caused by citing superseded or withdrawn editions are proactively flagged.
- Explainability: Every status, supersession link, and amendment diff includes traceable source provenance.
- Performance: Sub-millisecond evaluation latency (< 0.5 ms) ensures real-time UI interactivity.

### Negative / Tradeoffs
- Requires ongoing ingestion and maintenance of BIS gazette orders and amendment tables.
- Incomplete records require user review due to intentional abstention.

## Legal Disclaimer
NORMVAULT is an engineering and procurement decision-support tool. It does not provide binding statutory interpretations or legal advice. All currentness findings should be verified against official BIS gazette notifications prior to contract execution.
