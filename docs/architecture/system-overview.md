# NORMVAULT Architecture: System Overview

## Problem Statement 26108 Context
**Smart India Hackathon Problem Statement 26108**:
> *"AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications."*

In public and defense procurement across India (including Government e-Marketplace - GeM, Indian Railways, CPWD, Defense PSUs), tender documents specify complex technical schedules. Determining the exact, legally binding Bureau of Indian Standards (BIS) specifications, allied test methods, mandatory Quality Control Orders (QCOs), and recent amendments is manually intensive, error-prone, and causes compliance delays or invalid procurements.

NORMVAULT is an enterprise-grade standards intelligence and recommendation engine engineered to bridge tender requirements directly to verified Indian Standards.

---

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT TIER                                     │
│  React + TypeScript + Vite + Tailwind CSS (Procurement & Compliance UI)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / JSON REST API
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                             API GATEWAY                                     │
│  FastAPI Application Layer (Pydantic v2 validation, CORS, Exception Handler) │
│  Routes: /health, /documents, /analysis, /standards, /compliance            │
└───────────────────┬───────────────────────────────────┬─────────────────────┘
                    │                                   │
┌───────────────────▼─────────────────┐   ┌─────────────▼─────────────────────┐
│      PROCUREMENT PIPELINE           │   │    STANDARDS INTELLIGENCE         │
│  - Document Ingestion (PDF/DOCX)    │   │  - BIS Gazette Ingestion Engine   │
│  - Multilingual NLP Parser          │   │  - Edition & Amendment Tracker    │
│  - Parameter Extractor (Dim/Mech)   │   │  - Normative Knowledge Graph      │
│  - Specification Gap Detection      │   │  - QCO Statutory Rule Engine      │
└───────────────────┬─────────────────┘   └─────────────┬─────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                           STORAGE & VECTOR TIER                             │
│  PostgreSQL 16 + pgvector                                                   │
│  - Relational Schema: Standards, Editions, Amendments, Clauses, QCOs        │
│  - Vector Indexes: HNSW / IVFFlat embeddings on standard clauses & specs    │
│  - Full-Text Search: Indian Standards bilingual titles and technical terms  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Architectural Principles & Seams

Applying the `codebase-design` and `domain-modeling` disciplines:

1. **Strict No Fake Data Policy**:
   - Zero synthetic standards are seeded into production tables.
   - All recommendations must point to verified, official BIS gazette records.
2. **Deep Module Design**:
   - Small interfaces at boundaries; high depth behind seams.
   - Example: `StandardsRetrieverProtocol` provides a minimal `.retrieve(query, limit)` interface hiding hybrid vector similarity, BM25 keyword matching, and knowledge graph traversal.
3. **Decoupled Lifecycle Management**:
   - Standards maintain a persistent identity (`IndianStandard`, e.g. `IS 4984`), while revision years (`StandardEdition`), amendments (`Amendment`), and cross-standard dependencies (`NormativeReference`) remain distinct first-class entities.
4. **Environment Agility**:
   - Configured for PostgreSQL 16 + `pgvector` with automated fallback to SQLite for local development, CI pipelines, and unit testing.
