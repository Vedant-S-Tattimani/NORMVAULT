# Data Model: Specification Gap & Readiness Assessment (Phase 7)

## 1. Overview

Phase 7 introduces formal schema entities to represent specification completeness, technical ambiguities, parameter contradictions, standard coverage, and overall procurement readiness.

```
┌─────────────────────────────────┐
│     ProcurementSpecification     │
└──────────────┬──────────────────┘
               │ 1:N
               ├─────────────────────────────────────────┐
               ▼                                         ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│        SpecificationGap         │       │ ProcurementReadinessAssessment  │
│                                 │       │                                 │
│ - id: int                       │       │ - id: int                       │
│ - specification_id: int         │       │ - specification_id: int         │
│ - requirement_id: int (opt)     │       │ - readiness_state: Enum         │
│ - gap_type: GapType             │       │ - completeness_score: float     │
│ - severity: GapSeverity         │       │ - expected_parameters_count: int│
│ - parameter_name: str           │       │ - present_parameters_count: int │
│ - original_text: str            │       │ - missing_parameters_count: int │
│ - reason: str                   │       │ - ambiguous_parameters_count:int│
│ - clarification_prompt: str     │       │ - conflicting_parameters_count  │
│ - standard_context: str         │       │ - critical_gaps_count: int      │
│ - created_at: datetime          │       │ - high_gaps_count: int          │
└─────────────────────────────────┘       │ - medium_gaps_count: int        │
                                          │ - low_gaps_count: int           │
                                          │ - rationale: str                │
                                          │ - assessment_metadata: JSONB    │
                                          │ - created_at: datetime          │
                                          └─────────────────────────────────┘
```

---

## 2. Enumerations

### 2.1 `GapType`
- `MISSING_PRIMARY_APPLICABILITY_PARAMETER`
- `MISSING_CORE_TECHNICAL_PARAMETER`
- `MISSING_ACCEPTANCE_CRITERIA`
- `MISSING_TEST_METHOD`
- `MISSING_SAFETY_REQUIREMENT`
- `MISSING_INSTALLATION_PRACTICE`
- `MISSING_ALLIED_INTERFACE`
- `MISSING_CERTIFICATION_REQUIREMENT`
- `AMBIGUOUS_SPECIFICATION`
- `NON_MEASURABLE_REQUIREMENT`
- `PARAMETER_CONFLICT`
- `EDITION_INCONSISTENCY`
- `SUPERSEDED_STANDARD_CITED`
- `UNVERIFIABLE_CLAIM`
- `UNINDEXED_AMENDMENT_IMPACT`
- `INFORMATIONAL_COMPLETENESS`

### 2.2 `GapSeverity`
- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`
- `INFO`
- `WARNING` (alias for backward compatibility)
- `INFORMATIONAL` (alias for backward compatibility)

### 2.3 `ReadinessState`
- `READY_FOR_PROCUREMENT`
- `CONDITIONAL_READINESS`
- `ACTION_REQUIRED_BEFORE_TENDER`
- `CRITICAL_AMBIGUITIES_DETECTED`
- `UNRESOLVED_STANDARD_CONTEXT`

### 2.4 `CompletenessCategory`
- `CORE_TECHNICAL`
- `PERFORMANCE`
- `ENVIRONMENTAL`
- `SAFETY_EARTHING`
- `CERTIFICATION_REGULATORY`

### 2.5 `CoverageStatus`
- `COVERED`
- `PARTIALLY_COVERED`
- `NOT_COVERED`
- `UNVERIFIABLE`

---

## 3. Database Tables

### 3.1 `specification_gaps`
Stores atomic gap records detected within a procurement specification or specific requirement clause.

| Column | Type | Nullable | Description |
|:---|:---|:---:|:---|
| `id` | `INTEGER` | No | Primary Key |
| `specification_id` | `INTEGER` | No | Foreign Key to `procurement_specifications.id` |
| `requirement_id` | `INTEGER` | Yes | Foreign Key to `requirements.id` |
| `gap_type` | `VARCHAR(64)` | No | Categorization of the gap |
| `severity` | `VARCHAR(32)` | No | Severity level |
| `parameter_name` | `VARCHAR(128)` | Yes | Physical parameter or subject area |
| `original_text` | `TEXT` | Yes | Verbatim snippet triggering the gap |
| `reason` | `TEXT` | No | Technical explanation of the deficiency |
| `clarification_prompt` | `TEXT` | Yes | Recommended tender clause phrasing |
| `standard_context` | `VARCHAR(128)` | Yes | Indian Standard reference |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | Creation timestamp |

### 3.2 `procurement_readiness_assessments`
Stores the holistic evaluation of a tender document.

| Column | Type | Nullable | Description |
|:---|:---|:---:|:---|
| `id` | `INTEGER` | No | Primary Key |
| `specification_id` | `INTEGER` | No | Foreign Key to `procurement_specifications.id` |
| `readiness_state` | `VARCHAR(64)` | No | Deterministic readiness verdict |
| `completeness_score` | `FLOAT` | No | Ratio of present / expected parameters |
| `expected_parameters_count` | `INTEGER` | No | Total normative baseline parameters |
| `present_parameters_count` | `INTEGER` | No | Unambiguously stated parameters |
| `missing_parameters_count` | `INTEGER` | No | Omitted baseline parameters |
| `ambiguous_parameters_count` | `INTEGER` | No | Subjective or non-measurable parameters |
| `conflicting_parameters_count` | `INTEGER` | No | Directly contradictory parameters |
| `critical_gaps_count` | `INTEGER` | No | Count of CRITICAL severity gaps |
| `high_gaps_count` | `INTEGER` | No | Count of HIGH severity gaps |
| `medium_gaps_count` | `INTEGER` | No | Count of MEDIUM severity gaps |
| `low_gaps_count` | `INTEGER` | No | Count of LOW severity gaps |
| `rationale` | `TEXT` | No | Human-readable explanation of the state |
| `assessment_metadata` | `JSONB` | Yes | Traceability, coverage, and context metadata |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | Creation timestamp |
