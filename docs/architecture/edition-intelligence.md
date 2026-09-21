# Architecture: Standard Edition & Currentness Intelligence

## 1. Overview & Problem Context
In Indian public and industrial procurement (Smart India Hackathon Problem Statement 26108), standard citation ambiguity is one of the leading causes of audit rejections, contract disputes, and non-compliant equipment delivery. A standard number (e.g. `IS 12615` or `IS 325`) evolves over decades across distinct publications, major revisions, reaffirmations, and statutory mandates.

A critical engineering principle governs NORMVAULT:
> **CRITICAL PRINCIPLE**: NEVER assume: `NEWEST EDITION = APPLICABLE EDITION`.

Procurement contracts frequently cite specific historical editions (e.g., `IS 325:1996`), or cite standards ambiguously without year qualifications (`IS 12615`), or present conflicting edition references across disparate tender clauses. Silently substituting a newer edition violates contractual fidelity; conversely, ignoring supersession or withdrawal risks statutory non-compliance under Bureau of Indian Standards (BIS) Quality Control Orders (QCOs).

The Edition & Currentness Intelligence Engine resolves standard editions, amendment chains, supersession relationships, and procurement warnings based exclusively on verified database provenance.

---

## 2. Standard Family vs. Edition Separation
A fundamental architectural requirement is decoupling the **Standard Family** from **Individual Editions**:
- **Standard Family (`IndianStandard`)**: Represents the persistent canonical identity and subject matter (e.g., `IS 12615` — Line Operated Three-Phase A.C. Motors).
- **Standard Edition (`StandardEdition`)**: Represents a specific publication event with fixed normative text, identified by its calendar year and edition number (e.g., `IS 12615:2018`, Edition 2; `IS 12615:2011`, Edition 1).

```
                      IndianStandard
                         IS 12615
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
  StandardEdition                         StandardEdition
    Year: 2011                              Year: 2018
  Status: SUPERSEDED                      Status: CURRENT
        │                                       │
  (No Amds)                               ┌─────┴─────┐
                                          ▼           ▼
                                      Amendment 1  Amendment 2
                                      (Clause 7.1) (Clause 8.3)
```

---

## 3. Edition States & Provenance
Every standard edition record maintains an explicit, evidenced lifecycle state:
- `CURRENT`: Actively in force, recognized by BIS as the valid standard.
- `SUPERSEDED`: Replaced by a subsequent edition or a restructured standard.
- `WITHDRAWN`: Officially cancelled by BIS without replacement or declared obsolete.
- `DRAFT`: Proposed standard undergoing public review or committee balloting.
- `UNKNOWN`: Insufficient metadata indexed in the database to establish status.

**Rule**: Status is never inferred from the publication year. A standard published in 1996 remains `CURRENT` unless an official supersession or withdrawal order is recorded with verified provenance.

---

## 4. Precedence & Multi-Tier Resolution Model
Edition resolution follows an auditable, deterministic 6-tier precedence hierarchy:

```
┌───────────────────────────────────────────────────────────┐
│ 1. Verified Explicit Tender Citation (e.g. IS 12615:2018) │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│ 2. Conflicting Tender Citation Detection                  │
│    (Flags CONFLICTING_EDITION_REFERENCES)                 │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│ 3. Statutory QCO Edition Mandate                          │
│    (Validates whether cited edition satisfies QCO)        │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│ 4. Verified Edition Status & Supersession Chain           │
│    (Checks if cited edition is SUPERSEDED or WITHDRAWN)   │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│ 5. Active Currentness Verification Evidence               │
│    (Assembles active amendment chain and clause diffs)    │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│ 6. Principled Abstention (CURRENTNESS_UNCERTAIN)          │
│    (Refuses to hallucinate status if records incomplete)  │
└───────────────────────────────────────────────────────────┘
```

---

## 5. Distinction: Technical Applicability vs. Edition Applicability
NORMVAULT rigorously decouples three dimensions of evaluation:
1. `TECHNICAL_APPLICABILITY`: Does the engineering scope, product definition, and operating parameter envelope match the tender requirement? (e.g. `APPLICABLE`).
2. `EDITION_APPLICABILITY`: Is the specific edition cited in the tender valid, superseded, or unspecified? (e.g. `EXPLICITLY_CITED_SUPERSEDED`).
3. `CERTIFICATION_CURRENTNESS`: Does the standard and edition satisfy mandatory statutory QCO orders? (e.g. `MANDATORY_QCO_MATCH`).

Example:
- Standard: `IS 325:1996`
- Technical Applicability: `APPLICABLE` (it defines three-phase induction motor parameters).
- Edition Applicability: `EXPLICITLY_CITED_SUPERSEDED` (superseded by `IS 12615:2018`).
- Procurement Warning: `"Procurement document explicitly cites IS 325:1996. A newer edition exists (IS 12615:2018). Review required."`

The engine never silently replaces `IS 325:1996` with `IS 12615:2018`. It informs procurement officers so contractual addenda can be issued transparently.
