# NORMVAULT

### Evidence-backed procurement intelligence for Indian Standards

NORMVAULT is an AI-powered procurement intelligence platform designed to analyze procurement specifications, identify potentially applicable Indian Standards, evaluate applicability using evidence, track standard editions and currentness, analyze dependencies and regulatory signals, detect specification gaps, and produce an explainable Procurement Decision Package.

> **Smart India Hackathon 2026 — Problem Statement 26108**
>
> AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications

---

## Overview

Procurement specifications often contain incomplete, ambiguous, conflicting, or insufficiently contextualized technical requirements.

Identifying the correct Indian Standards is not simply a semantic search problem.

A reliable system must consider:

- the actual procurement requirement
- product and application context
- standard scope
- technical parameters
- explicit exclusions
- referenced standards
- normative dependencies
- standard editions
- amendments
- supersession and withdrawal
- certification requirements
- regulatory and QCO evidence
- missing or conflicting specification information
- provenance and source evidence

NORMVAULT approaches this as an evidence-driven decision-support problem.

The system combines deterministic domain logic, hybrid retrieval, document intelligence, standards knowledge, dependency analysis, currentness intelligence, and explainable decision packaging.

---

# Core Principles

NORMVAULT follows several non-negotiable principles.

### Evidence over assertion

Every important determination should be traceable to supporting evidence.

### Retrieval is not applicability

A semantically similar standard is only a candidate.

Retrieval signals do not automatically establish applicability.

### Missing information is not non-compliance

A specification gap is explicitly represented as a gap or uncertainty rather than being incorrectly classified as non-compliant.

### Newest edition is not automatically applicable

Edition selection considers the procurement context, explicit citations, currentness, amendments, supersession, and regulatory evidence.

### Referenced does not automatically mean mandatory

Technical references and statutory/regulatory obligations are kept separate.

### No fabricated data

NORMVAULT does not fabricate standards, clauses, regulatory requirements, applicability conclusions, or evidence when the required information is unavailable.

### Human review remains explicit

Where evidence is insufficient or contradictory, the system surfaces uncertainty and review actions rather than silently making an unsupported determination.

---

# What NORMVAULT Does

## 1. Specification Analysis

Procurement specifications can be submitted for structured analysis.

The system identifies requirements and preserves evidence such as:

- exact source text
- page
- section
- document location
- technical parameters
- requirement type

---

## 2. Hybrid Standards Retrieval

NORMVAULT uses a hybrid retrieval pipeline combining:

- lexical retrieval
- semantic retrieval
- reciprocal rank fusion
- metadata filtering
- deterministic reranking
- evidence extraction

The retrieval layer produces candidate standards.

It does not independently declare them applicable.

---

## 3. Applicability Analysis

Candidate standards are evaluated against procurement requirements using an evidence matrix.

The system considers:

- scope match
- product match
- parameter match
- application match
- explicit references
- exclusions
- negative evidence
- evidence alignment

Possible decisions include:

```text
APPLICABLE
POSSIBLY_APPLICABLE
NOT_APPLICABLE
INSUFFICIENT_EVIDENCE
```

---

## Strict Engineering Principles

1. **No Fake Data Policy**: Zero synthetic Indian Standards or mock AI recommendations are presented. The database reflects strictly verified gazette publications and standards metadata.
2. **Deep Domain Modeling**: Explicitly separates canonical **Standards** from **Standard Editions**, **Amendments**, and **Normative References**, preventing obsolete editions from passing compliance unnoticed.
3. **Enterprise Procurement UI**: Restrained, accessible, high-density interface built with React, TypeScript, and Tailwind CSS. Avoids flashy AI gimmicks, glowing decorations, and fake statistics.
4. **Resilient Data Architecture**: Built for PostgreSQL 16 + `pgvector` with zero-friction SQLite fallback for local development and CI testing.

---

## Monorepo Architecture

```
normvault/
│
├── apps/
│   ├── frontend/                # Vite + React 18 + TypeScript + Tailwind CSS
│   │   ├── src/components/      # Accessible enterprise components (Badge, Card, AppShell, Header)
│   │   ├── src/pages/           # Dashboard, Specification Intake, Standards Registry, Compliance
│   │   ├── src/services/        # Typed API clients (healthService, standardsService)
│   │   └── src/types/           # TypeScript domain definitions matching Pydantic schemas
│   │
│   └── backend/                 # FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Alembic
│       ├── app/api/routes/      # Health, Documents, Analysis, Standards, Recommendations, Compliance
│       ├── app/core/            # Pydantic Settings, structured logging, security limits
│       ├── app/db/              # SQLAlchemy session, engine pooling, pgvector support
│       ├── app/models/          # Domain models (Standard, Edition, Amendment, Clause, Reference, etc.)
│       ├── app/schemas/         # Typed request/response validation schemas
│       └── app/services/        # Abstract protocols for parsing, extraction, retrieval, and graph
│
├── data/                        # raw/, processed/, standards/, evaluation/
├── knowledge/                   # standards/, relationships/, certifications/, amendments/
├── scripts/                     # Ingestion, indexing, evaluation, and maintenance utilities
├── docs/                        # Architecture overview, domain model, API conventions, ADRs
│   ├── architecture/            # system-overview.md
│   ├── data-model/              # domain-model.md
│   ├── api/                     # api-conventions.md
│   └── decisions/               # Architecture Decision Records (0001, 0002)
├── tests/                       # E2E and multi-layer test suites
├── .env.example                 # Root configuration template
├── docker-compose.yml           # PostgreSQL 16 + pgvector container configuration
├── CONTEXT.md                   # Ubiquitous language glossary (DDD)
└── README.md
```

---

## Getting Started

### Prerequisites
- **Node.js**: v18+ (tested on Node v26.7.0, npm 12.0.2)
- **Python**: 3.11+ (tested on Python 3.12.10, uv 0.12.5)
- **Docker** (Optional, for PostgreSQL + pgvector container)

---

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd apps/backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   # Using uv (recommended)
   uv venv --python 3.12 .venv
   uv pip install -e ".[dev]"

   # Or using standard pip
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # source .venv/bin/activate # Linux/macOS
   pip install -e ".[dev]"
   ```

3. Run backend unit and model tests:
   ```bash
   pytest
   ```

4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - API Root: `http://127.0.0.1:8000/`
   - Health Diagnostics: `http://127.0.0.1:8000/api/v1/health`
   - Interactive OpenAPI Docs: `http://127.0.0.1:8000/api/v1/docs`

---

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd apps/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run TypeScript type checks and production build:
   ```bash
   npm run typecheck
   npm run build
   ```

4. Launch Vite development server:
   ```bash
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
   - Application URL: `http://127.0.0.1:5173/`

---

### Containerized Database (PostgreSQL + pgvector)

To run the production database with pgvector support:
```bash
docker-compose up -d postgres
```

Update your `.env` to point to PostgreSQL:
```env
DATABASE_URL="postgresql+psycopg://normvault:normvault@localhost:5432/normvault"
```

---

## Verification & Test Results

- **Backend Pytest Suite**: **161/161 tests passing** across 27 test modules:
  - Adversarial prompt-injection defense & Unicode sanitization (`test_adversarial_defense.py`)
  - Hybrid standards retrieval & synthetic evaluation benchmarks (`test_retrieval.py`, `test_retrieval_benchmarks.py`)
  - Deterministic 8-point standards applicability matrix (`test_applicability.py`, `test_applicability_benchmarks.py`)
  - Edition currentness, amendments, and supersession adjudication (`test_currentness.py`, `test_currentness_benchmarks.py`)
  - Normative reference dependency trees & test standard tracking (`test_dependencies.py`, `test_dependency_benchmarks.py`)
  - Specification gap analysis & pre-tender corrigenda generation (`test_gap_analysis.py`, `test_gap_benchmarks.py`)
  - Procurement Decision Package generation & multi-view projections (`test_intelligence.py`, `test_intelligence_benchmarks.py`)
  - Document parsing & cryptographic offset provenance (`test_provenance.py`, `test_phase2_documents.py`)
  - Ingestion pipeline & database upserts (`test_ingestion_pipeline.py`)
- **Frontend Typecheck & Build**: Zero TypeScript compilation errors; Vite production bundle builds in under 3 seconds.
- **Continuous Integration (CI)**: Automated GitHub Actions workflow (`.github/workflows/ci.yml`) runs the full pytest test suite and frontend build matrix.
- **Seeded Standards Database**: `apps/backend/normvault_dev.db` contains 13 Indian Standards, 26 clauses, 14 normative references, 5 tenders, 9 extracted requirements, and 9 actionable gaps.

---

## Roadmap

| Phase | Focus | Status |
| :--- | :--- | :--- |
| **Phase 0** | **Engineering Foundation, Domain Models, Monorepo, Backend API, Frontend Shell, Tests** | **COMPLETE** |
| **Phase 1** | **BIS Standards Ingestion, Gazette Crawlers, Tender Document Parsing (PDF/TXT), Data Catalog** | **COMPLETE** |
| **Phase 2** | **NLP Requirement & Parameter Extraction Engine with Cryptographic Offsets & Adversarial Defense** | **COMPLETE** |
| **Phase 3** | **Hybrid Dense + BM25 Lexical Retrieval, Evidence Scoring & Standards Knowledge Graph** | **COMPLETE** |
| **Phase 4** | **Mandatory QCO Validation, Specification Gap Detection, Decision Package Multi-Views & GeM/CSV Export** | **COMPLETE** |

---

## License
Confidential · Developed for Smart India Hackathon 2024.
