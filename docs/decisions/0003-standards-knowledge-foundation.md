# 3. Standards Knowledge Foundation and Provenance Tracking

Date: 2026-09-19

## Status
Accepted

## Context
Phase 0 established the monorepo and initial domain models. For Phase 1, we must build out the "Standards Knowledge Foundation". A critical requirement of NORMVAULT is **Data Honesty**: the system must never fabricate standards or recommendations. LLMs cannot be trusted as primary data stores. Every piece of metadata must be traceable. Furthermore, clauses within standards have hierarchical relationships (e.g., Clause 4.1 belongs to Clause 4).

## Decision
1. **Provenance Model:** We will introduce a `ProvenanceRecord` domain model. All knowledge graph entities (`IndianStandard`, `StandardEdition`, `Amendment`, `Clause`, `NormativeReference`) will hold a foreign key (`provenance_id`) to this record.
2. **Clause Hierarchy:** The `Clause` model will be updated with a self-referencing `parent_clause_id` to represent the natural tree structure of standards documents.
3. **Ingestion Boundary:** All data ingestion logic will be strictly isolated to `scripts/ingestion/` using a `Normalization -> Validation -> Resolution` pattern, ensuring the main FastAPI application remains untouched by messy data processing logic.

## Consequences
### Positive
- Guarantees 100% traceability for all standards data, satisfying the "Data Honesty" requirement.
- Enables the UI to display confidence scores and source links for every extracted clause.
- Protects the core FastAPI application from the complexities of PDF parsing and web scraping.

### Negative
- Increases database complexity (more foreign keys).
- Ingestion scripts require careful orchestration to ensure `ProvenanceRecord`s are created before the domain entities.
