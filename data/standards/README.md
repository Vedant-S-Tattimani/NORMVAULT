# NORMVAULT Authoritative Standards Catalog & Ingestion

This directory contains structured Bureau of Indian Standards (BIS) datasets with edition history, normative cross-references, technical clauses, and statutory Quality Control Orders (QCO).

## Catalog Datasets

| File | Standard Number | Edition / Year | Division | Mandatory QCO | Key Mandates |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `IS_12615_2018.json` | **IS 12615** | Third Revision (2018) | ETD | DPIIT Electric Motors QCO 2024 | Minimum IE3 Premium Efficiency, 415V standard, IS 15999 test method |
| `IS_1786_2008.json` | **IS 1786** | Fourth Revision (2008/2023) | CED | Ministry of Steel QCO 2024 | Grade Fe 500D high ductility rebar, C ≤ 0.25%, mandatory rebend test |
| `IS_732_2019.json` | **IS 732** | Fourth Revision (2019) | ETD | CEA Safety Regulations | Mandatory 30 mA RCD shock protection, Type 2 SPDs, IEC 60364 alignment |

## Ingesting Standards into NORMVAULT

To import any standard JSON dataset into the active database, execute:

```bash
cd apps/backend
.\.venv\Scripts\python.exe -m app.cli.ingest_standard --file ..\..\data\standards\IS_12615_2018.json
```

The CLI performs idempotent upsertion:
1. Creates or updates the `IndianStandard` entry and division metadata.
2. Ingests edition revisions and supersession links.
3. Ingests hierarchical technical clauses with verbatim text.
4. Generates normative dependency edges in the database graph.
