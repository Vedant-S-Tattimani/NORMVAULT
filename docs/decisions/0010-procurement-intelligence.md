# ADR 0010: Procurement Intelligence & Explainable Decision Package Engine

## Status
Accepted

## Context
Across Phases 2 to 7, NORMVAULT developed sophisticated specialized engines:
- Document intelligence and requirement extraction (Phase 2)
- Hybrid retrieval with candidate fusion (Phase 3)
- Applicability analysis with negative evidence preservation (Phase 4)
- Standards dependency and compliance intelligence (Phase 5)
- Standard edition, amendment, and currentness verification (Phase 6)
- Specification gap detection and procurement readiness (Phase 7)

Procurement officers and tender committees require a single, consolidated, explainable, and reproducible decision package that synthesizes all findings into actionable review recommendations without statistical confabulation, fabricated citations, or autonomous legal claims.

## Decision
1. **Unified Top-Level Model:** Create `ProcurementIntelligenceRun` and `ProcurementReviewAction` models storing versioning, configuration, and audit metadata.
2. **Deterministic Precedence Precedence:** Implement strict action priority precedence (`BLOCKING` > `HIGH` > `MEDIUM` > `LOW`) based on technical risk to tender validity and objective acceptance.
3. **No Arbitrary Percentages:** The Executive Summary and decision packages use verified facts, counts, clause citations, and deterministic states, completely rejecting ungrounded confidence percentages.
4. **Grounded Verification Guard:** Require all citations (standards, editions, clauses, QCO notifications) to be cross-verified against active database records before presentation.
5. **Adversarial Prompt Injection Defense:** Treat tender documents as untrusted data, neutralizing adversarial directives while preserving deterministic analysis.
6. **Multi-View Projections:** Provide 6 tailored views (`FULL_ANALYSIS`, `EXECUTIVE_SUMMARY`, `TECHNICAL_REVIEW`, `REGULATORY_REVIEW`, `TRACEABILITY_REPORT`, `CLARIFICATION_LIST`) from the single canonical evidence structure.
7. **Advisory Decision-Support Boundary:** Formally document and enforce that NORMVAULT provides decision support and does not claim legal compliance or guarantee tender validity.

## Consequences
### Positive
- A single canonical API response satisfies all downstream consumer needs (frontend, CLI, export).
- 100% reproducible analysis runs backed by SHA-256 document hashing and version tracking.
- Complete auditability from tender text to standards clause, dependency, gap, and review action.
- Sub-60ms orchestration latency ensuring instant interactive feedback.

### Negative / Trade-offs
- The decision package is a large payload when viewed in `FULL_ANALYSIS` mode; mitigated by providing filtered stakeholder view projections.
