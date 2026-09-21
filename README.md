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
