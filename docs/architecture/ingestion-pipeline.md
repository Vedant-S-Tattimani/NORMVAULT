# Ingestion Pipeline Architecture

The NORMVAULT ingestion pipeline (`scripts/ingestion/`) is responsible for translating messy, real-world standards data (PDFs, scraped HTML, legacy CSVs) into our strict, provenance-backed Domain Model.

## Core Philosophy: Deterministic and Traceable
The pipeline MUST be separated from the operational API backend. It runs asynchronously or via scheduled jobs, ensuring the production database only contains validated data.

## Pipeline Stages

### 1. Extraction
Fetching raw data from sources (BIS portal, PDFs).
- **Output:** Raw bytes, text, or unvalidated JSON.

### 2. Normalizers (`scripts/ingestion/normalizers.py`)
Transforming raw text into structured but unvalidated dictionaries.
- Example: Regex extraction of clause numbers from PDF text.
- Example: LLM structured extraction (with strict JSON schemas) to parse tables.

### 3. Validators (`scripts/ingestion/validators.py`)
Ensuring the normalized data conforms to business rules.
- Example: Checking that an Edition Year is realistic (e.g., > 1940 and <= Current Year).
- Example: Verifying that `StandardNumber` matches the `IS [number]` pattern.
- This layer uses Pydantic heavily.

### 4. Resolvers (`scripts/ingestion/resolvers.py`)
Mapping validated data into the database models and resolving foreign key relationships.
- Example: Looking up the canonical `IndianStandard.id` before inserting a new `StandardEdition`.
- Example: Generating the `ProvenanceRecord` before committing the transaction.

## Folder Structure
```
scripts/ingestion/
├── normalizers.py   # Regex, text cleanup, structural normalization
├── validators.py    # Pydantic schemas for intermediate validation
├── resolvers.py     # SQLAlchemy DB insertion and relationship mapping
└── main_ingest.py   # CLI entrypoint for ingestion jobs
```
