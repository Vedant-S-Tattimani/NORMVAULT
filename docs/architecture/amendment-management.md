# Architecture: Amendment Management & Clause Impact Analysis

## 1. Overview
In the Bureau of Indian Standards (BIS) governance system, standards are frequently amended between major revisions to adjust test tolerances, update normative cross-references, expand scope, or refine safety criteria. An amendment does not produce a new edition; it modifies specific clauses within an existing parent edition.

The Amendment Management Engine preserves the historical integrity of parent editions while tracking active amendment sequences and providing clause-level impact analysis.

---

## 2. Amendment Model & Attachment
Each amendment record is anchored directly to its parent `StandardEdition`:
- `amendment_number`: Integer sequential index (e.g. 1, 2, 3).
- `edition_id`: Foreign key pointing to the exact `StandardEdition`.
- `title` / `summary`: Official description of the amendment purpose.
- `issue_date` / `effective_date`: Enactment and gazette notification timeline.
- `affected_clauses`: Normalized list of impacted clauses (e.g. `Clause 7.1`, `Clause 8.3`).
- `old_clause_text`: Verified pre-amendment clause text.
- `new_clause_text`: Verified post-amendment clause text.
- `clause_impact_summary`: Qualitative explanation of the engineering consequence.
- `is_effective`: Boolean flag indicating active statutory or normative status.
- `provenance_id`: Full traceability to gazette or BIS catalog records.

---

## 3. The Amendment Chain
Amendments form a chronological modification chain:

```
Standard Edition 2018 (Base Text)
         │
         ▼
    Amendment 1 (Effective: 2019)
    - Affected: Clause 7.1
    - Delta: Tightened efficiency tolerance from -15% to -10% for >= 0.75 kW
         │
         ▼
    Amendment 2 (Effective: 2021)
    - Affected: Clause 8.3
    - Delta: Terminal box marking & earthing lug specifications updated
```

Crucially:
- Base edition text is never overwritten or mutated destructively.
- Historical evaluation remains reproducible for older contracts.
- Cumulative amendments are sequenced deterministically.

---

## 4. Clause Impact Analysis & Unindexed State Handling
When a procurement tender cites a standard or when applicability analysis maps tender parameters to standard clauses, the engine correlates affected clauses against active amendments:

### Scenario A: Clause Text & Delta Indexed
When verified clause text before and after the amendment exists:
- Side-by-side or stacked diff rendering is generated.
- Verified excerpt is highlighted:
  - Previous text: `"Tolerance on efficiency shall be -15% of (100 - Efficiency)."`
  - Amended text: `"Tolerance on efficiency shall be -10% of (100 - Efficiency) for motors >= 0.75 kW."`
  - Impact statement: `"Tightened efficiency measurement tolerance for IE3 class."`

### Scenario B: Unindexed Clause Text (Zero Fabrication Policy)
If an amendment is officially recorded in the BIS catalog but the detailed clause delta text has not yet been digitized into the knowledge base:
- **STRICT RULE**: The system never hallucinates or fabricates old/new text.
- The engine explicitly emits:
  > `"Amendment identified; clause impact not indexed."`
- The user is alerted that Amendment 2 is active and affects Clause 8.3, but manual verification of physical BIS gazette text is required.
