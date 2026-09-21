# Data Model: Standard Edition, Amendments & Currentness Entities

## 1. Relational Schema Overview
The Phase 6 data model enriches the foundational entities (`IndianStandard`, `StandardEdition`, `Amendment`, `CertificationRequirement`, `NormativeReference`) with explicit lifecycle states, supersession links, withdrawal metadata, and edition-bound dependencies.

---

## 2. Entity Specifications

### `StandardEdition`
Represents an immutable publication instance of an Indian Standard.
- `id`: Primary key (Integer).
- `standard_id`: Foreign key to `IndianStandard.id`.
- `edition_number`: Sequential edition index (e.g. 1, 2, 3).
- `year`: Calendar publication year (e.g. 2018).
- `status`: Enum (`CURRENT`, `SUPERSEDED`, `WITHDRAWN`, `DRAFT`, `UNKNOWN`).
- `is_current`: Boolean cache for fast active lookup.
- `reaffirmation_year`: Optional year of BIS technical reaffirmation.
- `superseded_date`: Date on which supersession became legally effective.
- `superseded_by_edition_id`: Optional self-referencing foreign key to `StandardEdition.id`.
- `superseded_by_standard_number`: Standard number of superseding standard (if standard family changed).
- `supersession_reason`: Official administrative or technical rationale.
- `supersession_evidence`: Source citation supporting supersession.
- `withdrawal_date`: Date on which standard was officially withdrawn.
- `withdrawal_reason`: Administrative justification for withdrawal.
- `withdrawal_evidence`: Citation supporting withdrawal order.
- `provenance_id`: Foreign key to `ProvenanceRecord.id`.
- Relationships:
  - `standard`: Many-to-one to `IndianStandard`.
  - `amendments`: One-to-many to `Amendment` (ordered by `amendment_number`).
  - `superseded_by`: Self-referencing relationship.

---

### `Amendment`
Represents an official modification enacted against a specific edition.
- `id`: Primary key (Integer).
- `standard_edition_id`: Foreign key to parent `StandardEdition.id`.
- `amendment_number`: Integer sequential index (e.g. 1, 2).
- `title`: Optional amendment title.
- `issue_date`: Date of issuance by BIS.
- `effective_date`: Date when enforcement commenced.
- `summary`: High-level summary of modifications.
- `affected_clauses`: Comma-separated or structured list of modified clauses (e.g. `"Clause 7.1, Clause 7.3"`).
- `old_clause_text`: Exact verbatim clause text before modification.
- `new_clause_text`: Exact verbatim clause text after modification.
- `clause_impact_summary`: Engineering impact explanation.
- `is_effective`: Boolean flag (true = active, false = superseded by later amendment).
- `provenance_id`: Foreign key to `ProvenanceRecord.id`.

---

### `CertificationRequirement` (Edition Enrichment)
Enriched to support edition-specific statutory mandates:
- `edition_id`: Optional foreign key to `StandardEdition.id`.
- `edition_year`: Optional explicit integer year mandated by QCO (e.g. 2018).
- `edition`: Many-to-one relationship to `StandardEdition`.

---

### `NormativeReference` (Edition Scoping)
Enriched to ensure dependencies do not leak across edition boundaries:
- `source_edition_id`: Optional foreign key to `StandardEdition.id`.
- `target_edition_year`: Optional integer year of referenced standard.
- `source_edition`: Many-to-one relationship to `StandardEdition`.

---

## 3. Pydantic Schemas
- `CurrentnessEvaluation`: Unified output containing resolution status, cited vs resolved edition years, amendment counts, supersession/withdrawal reasons, QCO match, procurement warning, and evidence summary.
- `StandardTimelineEvent`: Individual event in the standard lifecycle (`year_or_date`, `event_type`, `title`, `description`, `evidence`).
- `StandardHistoryRead`: Comprehensive chronological history containing standard identity, all editions with statuses, amendment counts, and ordered timeline events.
- `EditionRead`: Serialized edition entity including embedded `AmendmentChainItem` list.
