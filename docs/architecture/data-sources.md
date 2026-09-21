# Data Sources

This document describes the primary data sources for Indian Standards ingested into the NORMVAULT platform.

## 1. Bureau of Indian Standards (BIS) Official Portal
- **Description:** The primary authoritative source for Indian Standards, QCOs (Quality Control Orders), and Amendments.
- **Data Extracted:** Standard numbers, titles, division codes, current status, edition years, amendment metadata, and mandatory certification requirements.
- **Reliability:** Highest. This is the canonical source of truth for the existence and metadata of a standard.
- **Format:** HTML, APIs (where available), and PDFs.

## 2. Standard Document PDFs
- **Description:** The actual published PDF documents containing the text of the standards, clauses, and normative references.
- **Data Extracted:** Clause hierarchy, clause text, tables, figures, embedded normative references (e.g., "Tested in accordance with IS 2530").
- **Reliability:** High, but prone to extraction errors due to OCR and layout complexities.
- **Format:** PDF.

## 3. Gazette Notifications (eGazette)
- **Description:** Official government gazette notifications containing Quality Control Orders (QCOs) and amendments.
- **Data Extracted:** Legal mandates, effective dates, superseded rules.
- **Reliability:** Highest (Legal).
- **Format:** PDF (often scanned images requiring OCR).

## 4. Manual Curation / Expert Override
- **Description:** Specific overrides or complex hierarchical mappings manually verified by domain experts.
- **Data Extracted:** Corrections to OCR errors, complex normative reference resolution, and semantic gap fixing.
- **Reliability:** Highest (Domain Expert).
- **Format:** JSON / CSV ingestion via `scripts/ingestion`.

> [!WARNING]
> **LLMs are NOT Data Sources**: LLMs are used for *extraction* and *normalization* of unstructured text, but they are NEVER considered a primary data source. Any data extracted by an LLM must have its provenance traced back to the original source document.
