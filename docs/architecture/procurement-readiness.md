# Architecture: Procurement Compliance Readiness Engine (Phase 7)

## 1. Executive Summary

The **Procurement Compliance Readiness Engine** synthesizes identified specification gaps into a holistic, deterministic procurement readiness assessment. It provides procurement officers, tendering authorities, and technical evaluation committees with actionable clarity on whether a tender specification is ready for publication or requires pre-tender remediation.

```
Specification Gaps (Phase 7) + Coverage Matrix
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│             Deterministic Readiness Evaluator            │
│                                                          │
│  State Machine Evaluation:                               │
│  - CRITICAL gaps present (Contradictions, QCO missing)   │
│    └─► ACTION_REQUIRED_BEFORE_TENDER                     │
│  - Subjective/vague phrases without measurable criteria  │
│    └─► CRITICAL_AMBIGUITIES_DETECTED                     │
│  - Missing test methods / non-standard ratings           │
│    └─► CONDITIONAL_READINESS                             │
│  - Candidate standards unverified / abstention           │
│    └─► UNRESOLVED_STANDARD_CONTEXT                       │
│  - All required parameters & references verified         │
│    └─► READY_FOR_PROCUREMENT                             │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│           Actionable Remediation Prioritization          │
│                                                          │
│  - Severity: CRITICAL > HIGH > MEDIUM > LOW > INFO       │
│  - Suggested Tender Addenda / Clarification Clauses      │
│  - Explainable Completeness Metrics                      │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
             ProcurementReadinessAssessment
```

---

## 2. Readiness States

The system defines 5 deterministic readiness states:

1. **`READY_FOR_PROCUREMENT`**:
   - Specification contains all essential technical parameters.
   - Measurable performance criteria and test methods are explicitly cited.
   - Statutory certification requirements (e.g. BIS QCO) are included.
   - No parameter conflicts or critical ambiguities exist.

2. **`CONDITIONAL_READINESS`**:
   - Primary technical ratings and standards are defined.
   - Minor gaps exist (e.g. omitted interface mounting standard `IS 1231` or advisory installation guidelines `IS 900`).
   - Tendering may proceed provided tender addenda or supplier clarifications are requested.

3. **`ACTION_REQUIRED_BEFORE_TENDER`**:
   - Direct physical parameter contradictions detected (e.g. conflicting voltages).
   - Mandatory statutory compliance requirement omitted (e.g. failure to mandate ISI mark under QCO).
   - Superseded standard editions cited that alter legal compliance.
   - Immediate technical revision required prior to publishing tender.

4. **`CRITICAL_AMBIGUITIES_DETECTED`**:
   - Critical performance aspects rely entirely on subjective adjectives (e.g. "heavy duty", "high quality", "suitable for harsh conditions").
   - Lack of objective thresholds renders vendor bids incomparable and acceptance testing legally unverifiable.

5. **`UNRESOLVED_STANDARD_CONTEXT`**:
   - Applicable Indian Standards could not be definitively resolved from current indexed records.
   - System principled abstention preventing false confidence.

---

## 3. Severity Classification Matrix

| Gap Type | Severity | Rationale |
|:---|:---:|:---|
| `PARAMETER_CONFLICT` | **CRITICAL** | Direct contradiction renders specification un-manufacturable. |
| `MISSING_CERTIFICATION_REQUIREMENT` | **CRITICAL** | Statutory non-compliance under Indian Law (QCOs). |
| `MISSING_PRIMARY_APPLICABILITY_PARAMETER`| **CRITICAL** | Core rating missing; cannot verify standard applicability. |
| `MISSING_TEST_METHOD` | **HIGH** | Performance cannot be verified during Factory Acceptance Testing. |
| `MISSING_SAFETY_REQUIREMENT` | **HIGH** | Non-compliance with mandatory earthing and electrical safety. |
| `SUPERSEDED_STANDARD_CITED` | **HIGH** | Legal tender risk citing withdrawn/superseded standards. |
| `AMBIGUOUS_SPECIFICATION` | **MEDIUM** | Subjective phrasing leads to tender disputes and bid variations. |
| `MISSING_ACCEPTANCE_CRITERIA` | **MEDIUM** | Lack of tolerance bounds creates ambiguity during inspection. |
| `MISSING_INSTALLATION_PRACTICE` | **MEDIUM** | Field commissioning risk without code of practice reference. |
| `MISSING_ALLIED_INTERFACE` | **LOW** | Mechanical mismatch risk (e.g. frame dimensions). |
| `UNINDEXED_AMENDMENT_IMPACT` | **LOW** | Minor amendment update advisories. |
| `INFORMATIONAL_COMPLETENESS` | **INFO** | Advisory enhancements for specification richness. |

---

## 4. Remediation Decision Support

For every detected gap, NORMVAULT produces an **Advisory Clarification Prompt**:
- Formatted as ready-to-use tender specification clauses.
- References precise Indian Standards, clauses, or tables.
- Eliminates subjective phrasing without assuming buyer intentions.
- Preserves buyer sovereignty while ensuring statutory and technical robustness.
