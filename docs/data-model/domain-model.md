# NORMVAULT Domain Model Specification

Established in accordance with the `domain-modeling` skill and DDD principles.

---

## 1. Ubiquitous Language & Core Entities

The NORMVAULT domain explicitly distinguishes between canonical standards, their historical editions, specific amendments, and cross-references.

```
                  ┌────────────────────┐
                  │   IndianStandard   │ (IS 4984)
                  └─────────┬──────────┘
                            │
       ┌────────────────────┼───────────────────┐
       │ 1..*               │ 1..*              │ 0..*
┌──────▼──────────┐  ┌──────▼──────────┐  ┌─────▼────────────────────┐
│ StandardEdition │  │    Amendment    │  │ CertificationRequirement │
│   (IS 4984:2016)│  │ (Amendment No.1)│  │ (ISI Mark / Mandatory QCO)│
└──────┬──────────┘  └─────────────────┘  └──────────────────────────┘
       │ 1..*
┌──────▼──────────┐
│     Clause      │ (Clause 4.2 Raw Material)
└─────────────────┘
```

### Entity Definitions

1. **IndianStandard**: The permanent legal identity of a Bureau of Indian Standards document (e.g. `IS 4984`, `IS 1786`). Does not change across revisions.
2. **StandardEdition**: A specific publication revision published in a given year (e.g., `IS 4984: 2016` vs `IS 4984: 1995`). Tracks whether it is the current prevailing edition or superseded.
3. **Amendment**: An official gazette notification that modifies, inserts, or deletes specific clauses in a standard without issuing a full revision.
4. **NormativeReference**: An explicit cross-standard dependency. Types include:
   - `NORMATIVE_REFERENCE`: General mandatory referenced document.
   - `TEST_METHOD`: Standard defining experimental procedure (e.g., `IS 2530`).
   - `ALLIED_PRODUCT`: Related system component (e.g., fittings for pipes).
   - `SAFETY_REQUIREMENT`: Mandatory occupational or industrial safety code.
   - `INSTALLATION_PRACTICE`: Laying, fitting, and commissioning code (e.g., `IS 7634`).
   - `SAMPLING_CRITERIA`: Quality inspection lot sizes and testing frequencies.
   - `SUPERSEDES`: Explicit replacement marker.
5. **Clause**: The atomic division of a standard containing technical prose, formulas, or dimensional tables. Holds the vector embedding for semantic search.
6. **CertificationRequirement**: Statutory conformity scheme (e.g. ISI Mark Scheme I, CRS Scheme II) and mandatory Quality Control Order (QCO) gazette references.
7. **ProcurementSpecification**: Ingested tender schedule, Bill of Quantities (BOQ), or technical annexure submitted by a procurement officer.
8. **Requirement**: Individual technical statement extracted from the procurement specification.
9. **TechnicalParameter**: Quantitative or qualitative attribute (e.g. parameter: `Tensile Strength`, operator: `>=`, value: `415`, unit: `MPa`).
10. **SpecificationAnalysis**: Container for an analysis run against a specification.
11. **Recommendation**: Match linking a specification to a primary or allied Indian Standard with confidence level and explainable rationale.
12. **RecommendationEvidence**: Fine-grained snippet connecting tender requirement text directly to the supporting standard clause.
13. **SpecificationGap**: Alert identifying tender deficiencies (e.g. citing an obsolete standard edition, missing statutory QCO clauses, or omitting mandatory test methods).

---

## 2. Relational Schema Summary

| Table Name | Entity | Key Foreign Keys |
| :--- | :--- | :--- |
| `indian_standards` | Canonical Standard | — |
| `standard_editions` | Revision Editions | `standard_id` → `indian_standards.id` |
| `standard_amendments` | Official Amendments | `standard_id` → `indian_standards.id` |
| `standard_clauses` | Individual Clauses | `edition_id` → `standard_editions.id` |
| `normative_references` | Typed Cross-Links | `source_standard_id`, `target_standard_id` |
| `certification_requirements` | QCOs & ISI schemes | `standard_id` → `indian_standards.id` |
| `procurement_specifications` | Tender Submissions | — |
| `spec_requirements` | Extracted Requirements | `specification_id` → `procurement_specifications.id` |
| `technical_parameters` | Quantitative Specs | `requirement_id` → `spec_requirements.id` |
| `specification_analyses` | Analysis Runs | `specification_id` → `procurement_specifications.id` |
| `analysis_recommendations` | Recommendations | `analysis_id`, `standard_id` |
| `recommendation_evidence` | Traceability Snippets | `recommendation_id`, `requirement_id`, `clause_id` |
| `specification_gaps` | Compliance Warnings | `analysis_id` → `specification_analyses.id` |
