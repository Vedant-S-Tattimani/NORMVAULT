# Architecture: Requirement Traceability & Coverage Matrix (Phase 7)

## 1. Executive Summary

The **Requirement Traceability and Coverage Matrix** subsystem bridges the gap between unstructured procurement text, extracted technical parameters, and normative Indian Standard clauses. It provides an end-to-end verifiable audit trail showing exactly how each tender requirement maps to applicable standards, which requirements are fully covered, and where verification gaps exist.

```
Procurement Specification Requirement
                 │
                 ├── Parameter Name & Value (Extracted)
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│              Traceability Builder Pipeline               │
│                                                          │
│  1. Parameter-Clause Mapping                             │
│     - Matches extracted parameters against Standard      │
│       clauses, tables, and limits.                       │
│                                                          │
│  2. Coverage Status Determination                        │
│     - COVERED: Parameter verified by standard clause     │
│     - PARTIALLY_COVERED: Standard covers concept but     │
│       tender omits required test method or bound         │
│     - NOT_COVERED: Parameter unaddressed by standard     │
│     - UNVERIFIABLE: Parameter uses subjective phrasing   │
│                                                          │
│  3. Graph Node Compilation                               │
│     - Requirement -> Standard -> Clause -> Verification  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│               Standard Coverage Matrix View              │
│                                                          │
│  - Tabular breakdown for procurement officers            │
│  - Clause-level references (e.g. Cl 6.2, Table 3)        │
│  - Clear actionable verification notes                   │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Coverage Statuses

1. **`COVERED`**:
   - The tender parameter is explicitly governed by an applicable Indian Standard clause.
   - Example: Voltage rating $415\text{ V}\pm 10\%$ is verified against `IS 12615:2018` Cl 6.1.

2. **`PARTIALLY_COVERED`**:
   - The standard provides guidance or classification, but the tender specification omits critical qualifying details.
   - Example: Tender specifies "IE3 efficiency" but fails to specify the test method standard (`IS 15999 (Part 2/Sec 1)`).

3. **`NOT_COVERED`**:
   - The parameter represents a custom or project-specific requirement not governed by the general product standard.
   - Example: Specific paint shade RAL 5012 or buyer-specific packing requirements.

4. **`UNVERIFIABLE`**:
   - The requirement is phrased with subjective adjectives lacking measurable physical thresholds.
   - Example: "Motor must have excellent cooling characteristics."

---

## 3. Data Flow and Graph Model

Every `TraceabilityNode` records:
- `requirement_id`: Link to Phase 2 `Requirement`.
- `requirement_text`: Original tender text.
- `standard_code`: Applicable Indian Standard (e.g. `IS 12615:2018`).
- `clause_number`: Normative clause governing the requirement.
- `parameter_name`: Normalized physical parameter.
- `coverage_status`: `CoverageStatus` enum value.
- `verification_method`: Routine test, Type test, FAT, or Certificate review.
- `notes`: Audit notes explaining verification basis.
