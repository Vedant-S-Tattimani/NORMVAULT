# 1. Monorepo Architecture & Technology Stack

Date: 2026-09-19

## Status
Accepted

## Context
NORMVAULT (Smart India Hackathon Problem Statement 26108) requires building a production-grade web application for Indian Standards intelligence in public procurement. The system requires tight coordination between:
1. An administrative/analyst web client for tender review.
2. A high-performance Python API for document parsing, NLP extraction, and semantic standards retrieval.
3. Verified Indian Standards catalogs, knowledge graphs, and benchmarks.

We needed to decide whether to separate the frontend, backend, and data pipelines into multi-repos or adopt a cohesive monorepo structure.

## Decision
We adopted a unified monorepo:
- `apps/frontend`: React 18, TypeScript, Vite, Tailwind CSS. Restrained, enterprise-grade procurement design system without decorative AI hypes.
- `apps/backend`: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0.
- `Database`: PostgreSQL 16 with `pgvector` as the production target; SQLite with pool ping for zero-friction local development and CI runs.
- `data/`, `knowledge/`, `scripts/`, `docs/`, `tests/` structured alongside the applications.

## Consequences
### Positive
- Shared domain models and synchronization between API schemas and TypeScript types.
- Single command workflows for local development and integration testing.
- Co-located documentation and data pipelines prevent architectural drift.

### Negative
- Monorepo requires discipline to avoid tight coupling between frontend utilities and backend dependencies.
