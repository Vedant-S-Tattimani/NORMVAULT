# Standards Knowledge Model

The NORMVAULT Standards Knowledge Model is a strict 4-tier domain hierarchy that accurately represents the lifecycle and structure of Indian Standards.

## Core Entities

### 1. Indian Standard
Represents the canonical identity of a standard (e.g., `IS 4984`). 
- **Attributes:** Standard number, title, scope, division code, department, status.

### 2. Standard Edition
Represents a specific dated revision (e.g., `IS 4984:2016`).
- **Attributes:** Edition number, year, is_current, superseded_date.
- **Relationship:** Belongs to one `IndianStandard`.

### 3. Amendment
Represents an official modification to specific clauses.
- **Attributes:** Amendment number, issue date, summary, affected clauses.
- **Relationship:** Belongs to an `IndianStandard`, optionally tied to a specific `StandardEdition`.

### 4. Clause
An atomic numbered section of a standard edition.
- **Attributes:** Clause number, title, content, is_normative, embedding_json.
- **Hierarchy:** Clauses can have a `parent_clause_id` to form a tree structure (e.g., Clause 4.1 is a child of Clause 4).
- **Relationship:** Belongs to a `StandardEdition`.

### 5. Normative Reference
A typed, directed relationship between two standards.
- **Attributes:** Relationship type (e.g., `TEST_METHOD`, `SAFETY_REQUIREMENT`), referencing clause.
- **Relationship:** Links a source `IndianStandard` to a target `IndianStandard`.

## Knowledge Graph Navigation
By separating canonical identities from editions, NORMVAULT enables true gap analysis. A tender might cite `IS 4984:1995`, but the knowledge graph knows that `IS 4984:2016` with `Amendment No. 2` is the current, active requirement.

> [!NOTE]
> All entities in the knowledge graph MUST link back to a `ProvenanceRecord` to guarantee traceability and data honesty.
