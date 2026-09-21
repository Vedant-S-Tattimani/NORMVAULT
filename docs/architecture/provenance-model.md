# Provenance Model

## Purpose
In a procurement intelligence application, data honesty is non-negotiable. NORMVAULT must never fabricate standards, clauses, or amendments. The `Provenance` model ensures that every piece of knowledge graph metadata is traceable back to its origin.

## The `ProvenanceRecord` Entity

Every major domain model (`IndianStandard`, `StandardEdition`, `Amendment`, `Clause`, `NormativeReference`) holds a foreign key to a `ProvenanceRecord`.

### Attributes
- **source_type (Enum):** E.g., `BIS_PORTAL`, `PDF_EXTRACTION`, `MANUAL_ENTRY`, `LLM_EXTRACTION`.
- **source_url (String):** URL to the original document or API endpoint (if applicable).
- **source_hash (String):** SHA-256 hash of the original source document to detect changes.
- **confidence_score (Float):** A value between 0.0 and 1.0 indicating extraction confidence. (1.0 for deterministic APIs, lower for OCR/LLM).
- **extraction_timestamp (DateTime):** When this data was ingested.
- **extraction_metadata (JSON):** Any additional raw context needed for debugging (e.g., raw OCR text, LLM prompt version).

## Implementation Rules
1. **Never mutate without Provenance:** Any script creating or updating a Standard entity MUST create or link to a `ProvenanceRecord`.
2. **LLM boundaries:** When an LLM extracts clauses from a PDF, the `source_type` is `LLM_EXTRACTION`, but the `source_url` MUST point to the original PDF, and the `confidence_score` must reflect the extraction certainty.

> [!IMPORTANT]
> The UI should eventually expose the Provenance data (e.g., an "i" icon next to a clause) so users can click and see exactly where that clause text came from, building trust in the system.
