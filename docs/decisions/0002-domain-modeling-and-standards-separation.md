# 2. Separation of Canonical Standards, Editions, Amendments, and References

Date: 2026-09-19

## Status
Accepted

## Context
A naive standards recommendation system treats a standard as a flat document (e.g., `{"name": "IS 4984"}`). However, in real Indian Standards procurement:
- Standard `IS 4984` has existed across multiple revisions (`IS 4984:1995`, `IS 4984:2016`).
- Gazette notifications publish amendments (`Amendment No. 1`, `Amendment No. 2`) that alter specific dimensional tolerances or test methods without reissuing the entire book.
- Procurement tenders frequently cite outdated editions or omit mandatory normative references (e.g. testing per `IS 2530` or installation practice per `IS 7634`).
- Collapsing these into a single "Standard" record makes it impossible to detect specification gaps or determine whether a supplier meets the latest prevailing legal edition.

## Decision
We established a strict 4-tier model hierarchy:
1. `IndianStandard`: Canonical BIS standard identity (number, title, scope, division).
2. `StandardEdition`: Specific revision year, edition number, and supersession timeline.
3. `Amendment`: Atomic amendments tracking affected clauses and gazette issue dates.
4. `NormativeReference`: Typed directed relationships (`TEST_METHOD`, `ALLIED_PRODUCT`, `SAFETY_REQUIREMENT`, `INSTALLATION_PRACTICE`, `SAMPLING_CRITERIA`).

## Consequences
### Positive
- Enables automated detection of tender gaps (e.g. tender citing a 1995 edition when a 2016 edition with Amendment 2 is mandatory).
- Enables accurate graph traversal from product standards to mandatory test methods.
- Mirrors actual Bureau of Indian Standards publishing and gazette notification lifecycles.

### Negative
- Requires ingestion scripts to parse clause-level amendment slips rather than treating PDFs as monolithic text chunks.
