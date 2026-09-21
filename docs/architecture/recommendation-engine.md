# Architecture: Standards Recommendation Engine (Phase 4)

## 1. Executive Summary

The **Standards Recommendation Engine** adjudicates between multiple candidate standards to produce transparent, traceable procurement recommendations. It distinguishes primary standards from secondary or alternative options and handles cases with ambiguous or insufficient specifications.

---

## 2. Decision Outcomes

The engine produces four canonical decision outcomes (`ApplicabilityOutcome`):

| Outcome | Definition | System Action |
| :--- | :--- | :--- |
| `APPLICABLE` | Strong verified scope alignment, exact/compatible product match, verified parameters, no fatal conflicts. | Tagged as either **Primary Recommended Standard** or **Alternative Candidate**. |
| `POSSIBLY_APPLICABLE` | Compatible product category and operating profile, but lacks specific sub-feature alignment or some parameters are unstated. | Designated as **Alternative Candidate** or part of **Multiple Plausible Standards**. |
| `NOT_APPLICABLE` | Fatal scope conflict, explicit domain exclusion, incompatible application, or out-of-range technical parameter. | Excluded from recommendations; negative evidence inspectable in UI. |
| `INSUFFICIENT_EVIDENCE` | Critical engineering parameters missing or standard scope unindexed, preventing deterministic adjudication. | Principled abstention; lists missing parameters and why they matter. |

---

## 3. Primary Standard vs Alternative Candidate Resolution

### 3.1 Decision Hierarchy
When multiple candidate standards evaluate to `APPLICABLE` or `POSSIBLY_APPLICABLE`, the engine does **not** rely on raw retrieval rank. Instead, it applies a deterministic evidence hierarchy:

1. **Explicit Tender Citation**: Direct citation in the tender (e.g. `"IS 12615"`) is assigned high evidence weight, though still verified against technical parameters.
2. **Specific Feature Scope Match**: A standard explicitly covering tender-specified sub-features (e.g. `IE3` efficiency class) wins over a broader standard (e.g. `IS 325`).
3. **Product Match Precision**: `EXACT` product match takes priority over generic `CATEGORY` match.
4. **Parameter Verification Depth**: Candidates with verified parameter compatibility receive higher alignment indices than unchecked candidates.

### 3.2 Tie-Breaking & Multiple Plausible Standards
If two standards share identical match levels and feature specificities (e.g., both match a generic "Three-phase motor" without efficiency codes):
- The engine abstains from arbitrary selection.
- Both candidates are labeled with the abstention reason `MULTIPLE_PLAUSIBLE_STANDARDS`.
- The engine explains what differentiating information (e.g., efficiency class, motor construction type) is needed to resolve between them.

---

## 4. Evidence Traceability & Auditability

Every recommendation records complete lineage:
- `retrieval_run_id`: The Phase 3 retrieval run that surfaced the candidate.
- `candidate_standard_id`: Unique identifier of the evaluated standard.
- `evidence_alignment_index`: Multi-criteria evidence score between 0.0 and 1.0.
- `reasons`: Machine-readable and human-readable evidence summaries.
- `conflicts`: Explicit list of identified conflicts, warnings, and exclusions.
- `missing_information`: Explicit list of absent specification attributes.
- `provenance`: Links to verified BIS scope clauses and edition metadata.
