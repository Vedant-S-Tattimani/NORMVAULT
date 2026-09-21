# Architecture: Procurement Decision Package

## 1. Overview

The **Procurement Decision Package** (`ProcurementDecisionPackageRead`) is the unified data structure emitted by NORMVAULT Phase 8. It consolidates all domain evidence, applicability determinations, currentness verifications, gaps, readiness assessments, review actions, and audit trails into a single canonical contract.

```
ProcurementDecisionPackage
├── run: ProcurementIntelligenceRunRead
├── executive_summary: ExecutiveSummaryRead
├── requirements_summary: List[RequirementRead]
├── standards_summary: StandardDecisionSummaryRead
├── edition_currentness: EditionCurrentnessSummaryRead
├── dependencies: DependencySummaryRead
├── qco_certification: QcoCertificationSummaryRead
├── gaps: GapSummaryRead
├── readiness: ProcurementReadinessAssessmentRead
├── actions: List[ProcurementReviewActionRead]
├── checklist: TenderReviewChecklistRead
├── clarifications: ClarificationPackageRead
├── traceability: TraceabilityReportRead
├── evidence_index: EvidenceIndexRead
└── limitations: List[SystemLimitationRead]
```

---

## 2. Package Sections

### 2.1 Executive Summary
Provides high-level situational awareness for procurement officers and tender committees:
- `procurement_title`: Official tender title or schedule description.
- `requirements_count`: Number of extracted requirements.
- `applicable_standards_count`: Number of confirmed applicable standards.
- `primary_standard`: Primary recommended standard (e.g., `IS 12615:2018`).
- `alternative_standards`: Viable alternative standards (e.g., `IS 325:1996`).
- `currentness_status`: Currentness verification (`CURRENT — VERIFIED`, `SUPERSEDED`, `WITHDRAWN`).
- `critical_gaps_count`: Number of blocking deficiencies.
- `high_gaps_count`: Number of high-severity technical gaps.
- `ambiguities_count`: Number of subjective or non-measurable requirements.
- `readiness_state`: Readiness state machine output (`READY_FOR_REVIEW`, `NEEDS_CLARIFICATION`, `TECHNICAL_GAPS_PRESENT`, `CRITICAL_INFORMATION_MISSING`, `UNRESOLVED_STANDARD_CONTEXT`).
- `summary_rationale`: Deterministic text explanation without arbitrary confidence percentages.

### 2.2 Standard Decision Summary
Preserves Phase 4 semantics and explains WHY each candidate received its designation:
- `primary_standard`: The standard with highest scope, product, parameter, and application alignment with zero fatal negative evidence.
- `alternative_candidates`: Standards applicable to subsets of requirements or legacy editions explicitly cited.
- `possibly_applicable`: Standards requiring further parameter clarification.
- `not_applicable`: Standards with explicit exclusions or negative scope evidence.
- `insufficient_evidence`: Standards where tender lack of detail prevented conclusive determination.

### 2.3 Edition & Currentness Summary
Details the standard family, edition year, edition status, amendments, supersession history, withdrawal status, and tender citation alignment.

### 2.4 Normative Dependencies & QCO
Categorizes all dependencies into:
- **Test Methods:** Standards for factory acceptance and type testing (e.g., IS 15999).
- **Safety Requirements:** Standards for electrical/mechanical safety and earthing (e.g., IS/IEC 60034-5, IS 3043).
- **Installation Practices:** Codes of practice for installation and commissioning (e.g., IS 900).
- **Allied Products:** Dimensional and mounting interface standards (e.g., IS 1231).
- **Statutory QCO:** Mandatory Quality Control Orders notified by Central Ministries under the BIS Act, 2016.

### 2.5 Prioritized Review Actions
Each action is derived from an evidence-backed gap or standards discrepancy:
- `priority`: `BLOCKING` > `HIGH` > `MEDIUM` > `LOW`
- `action_type`: 12 explicit categories (e.g., `CLARIFY_REQUIREMENT`, `RESOLVE_CONFLICT`, `VERIFY_STANDARD_EDITION`, `VERIFY_QCO`)
- `description`, `reason`, `suggested_action`, `source_gap_id`, `evidence`.

### 2.6 Tender Review Checklist & Clarification Package
- **Checklist:** Deterministic checkboxes evaluating technical completeness.
- **Clarification Questions:** Structured questions to be asked to the bidder or requisitioning department before tender finalization.

### 2.7 Traceability & Evidence Index
- **Traceability:** Complete end-to-end chain: Tender Text → Requirement → Parameter → Standard → Edition → Clause → Dependency → Gap → Action.
- **Evidence Index:** Inverted index listing every evidence ID, source URL, SHA-256 hash, and verification timestamp.

---

## 3. Stakeholder View Projections

The Decision Package supports 6 canonical view projections without duplicating underlying logic:
1. `FULL_ANALYSIS`: Complete package with all sections.
2. `EXECUTIVE_SUMMARY`: High-level summary, primary standards, and readiness.
3. `TECHNICAL_REVIEW`: In-depth parameters, dependencies, test methods, and gaps.
4. `REGULATORY_REVIEW`: QCO enforcement, mandatory certification schemes, and edition currentness.
5. `TRACEABILITY_REPORT`: Complete end-to-end traceability matrix.
6. `CLARIFICATION_LIST`: Formatted questions for requisitioning authority.
