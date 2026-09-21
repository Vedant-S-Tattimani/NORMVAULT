# NORMVAULT Data Directory

This directory stores raw and processed datasets for Indian Standards (Bureau of Indian Standards - BIS), tender documents, and evaluation benchmarks.

## Policy: Strict No Fake Data
- All data stored in `standards/` must originate from verified BIS gazettes, public catalogs, or official portals.
- Synthetic or benchmark testing specifications must be segregated in `evaluation/` and labeled as test fixtures.

## Structure
- `raw/`: Unprocessed PDF/DOCX procurement tenders and standards documents.
- `processed/`: Extracted text, cleaned clauses, and structured JSON representations.
- `standards/`: Verified Indian Standards catalogs and metadata.
- `evaluation/`: Gold-standard benchmark query-standard evaluation pairs.
