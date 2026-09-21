# Decision: Architectural Design of Specification Gap Analysis & Compliance Readiness Engine

- **Status**: Accepted
- **Deciders**: NORMVAULT Engineering Core Team
- **Date**: 2026-09-21
- **Context**: SIH Problem Statement 26108 (NORMVAULT Phase 7)

---

## 1. Context and Problem Statement

Procurement specifications across public sector undertakings (PSUs), government departments (GeM), and industrial organizations frequently suffer from incomplete parameter definitions, subjective or ambiguous phrasing, internal contradictions, omitted factory acceptance test methods, and failure to cite mandatory Quality Control Orders (QCOs).

Traditional tools either perform naive keyword matching or generate unconstrained LLM summaries that hallucinate technical ratings (e.g. turning "harsh environment" into "IP65" without evidence). 

We need a deterministic, explainable, and zero-hallucination engine to evaluate procurement specifications for technical completeness, ambiguity, contradictions, and readiness for tendering.

---

## 2. Considered Alternatives

1. **Option 1: End-to-End Generative LLM Summarization**
   - *Pros*: Quick to implement; produces fluent summaries.
   - *Cons*: High risk of hallucination (fabricating parameters), uncalibrated confidence percentages, vulnerable to prompt injection, high per-call cost and latency (>2000 ms), non-deterministic outputs.
2. **Option 2: Pure Regular Expression Keyword Matching**
   - *Pros*: Extremely fast (<1 ms), deterministic.
   - *Cons*: Cannot analyze multi-clause contradictions, cannot evaluate normative reference trees or dependency gaps, brittle against varying tender terminology.
3. **Option 3: Hybrid Deterministic Gap Detection & Standards-Grounded Readiness Engine (Selected)**
   - *Pros*: Combines normative product baselines with deterministic conflict/ambiguity detection, explains exact parameter counts (expected, present, missing, ambiguous, conflicting), guarantees zero hallucination, executes in <25 ms, provides structured clarification prompts for tender addenda.
   - *Cons*: Requires curated normative parameter baselines per product category.

---

## 3. Decision Outcome

We selected **Option 3: Hybrid Deterministic Gap Detection & Standards-Grounded Readiness Engine**.

### Key Architectural Commitments:
1. **Never Equate "Missing" with "Non-Compliant"**: Explicitly categorize gaps into `MISSING`, `AMBIGUOUS`, `CONFLICTING`, `UNVERIFIABLE`, `RECOMMENDED_FOR_CLARIFICATION`, `REQUIRED_FOR_STANDARD_VERIFICATION`, `REQUIRED_FOR_ACCEPTANCE_TEST`, and `REQUIRED_FOR_CERTIFICATION`.
2. **Deterministic Readiness State Machine**: Assign one of 5 explicit states (`READY_FOR_PROCUREMENT`, `CONDITIONAL_READINESS`, `ACTION_REQUIRED_BEFORE_TENDER`, `CRITICAL_AMBIGUITIES_DETECTED`, `UNRESOLVED_STANDARD_CONTEXT`).
3. **Explainable Completeness Metrics**: Replace arbitrary percentage scores with transparent counts (`expected_count`, `present_count`, `missing_count`, `ambiguous_count`, `conflicting_count`).
4. **Prioritized Remediation Prompts**: Provide procurement officers with exact, standards-grounded tender clause language to rectify each detected gap.
5. **Prompt Injection Hardening**: Treat tender documents as untrusted data, sanitizing adversarial tokens before analysis.

---

## 4. Consequences

### Positive:
- Total elimination of hallucinated technical parameters.
- High-speed sub-25ms end-to-end evaluation latency.
- Full auditability of all gaps back to specific tender text and Indian Standard clauses.
- Zero false "non-compliance" accusations against incomplete tenders.

### Negative / Trade-offs:
- Product baselines must be maintained and expanded as new equipment categories are onboarded to NORMVAULT.
