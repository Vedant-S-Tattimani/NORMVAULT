# Architecture: Applicability Analysis Engine (Phase 4)

## 1. Executive Summary

The **Applicability Analysis Engine** is Phase 4 of NORMVAULT (SIH Problem Statement 26108). Its objective is to transform Phase 3 Candidate Standards and Phase 2 structured procurement requirements into evidence-first, legally and technically grounded applicability assessments.

```
Requirements + Technical Parameters (Phase 2)
                 │
                 ▼
     Candidate Standards (Phase 3)
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│              Evidence-First Analysis Pipeline            │
│                                                          │
│  1. Scope Analysis (ScopeAnalyzer)                       │
│     - Scope coverage & specific feature detection (IE3)  │
│     - Exclusionary scope clause detection                │
│                                                          │
│  2. Product Matching (ProductMatcher)                    │
│     - Target product name vs Standard title & scope      │
│     - Match levels: EXACT, CATEGORY, AMBIGUOUS, MISMATCH │
│                                                          │
│  3. Application Compatibility (ApplicationMatcher)       │
│     - Duty cycle & operating environment matching        │
│     - Domestic vs Industrial vs Marine conflict detection │
│                                                          │
│  4. Parameter Verification (ParameterComparator)         │
│     - Compares quantitative bounds (kW, V, Hz, PN, MPa)  │
│     - Strict zero-fabrication: only verified bounds used │
│                                                          │
│  5. Tender Citation Handling (CitationHandler)           │
│     - Explicit 'IS XXXX' tenders tagged as high-value    │
│     - Does not silently override technical verification  │
│                                                          │
│  6. Missing Information Detection (MissingInfoDetector)  │
│     - Identifies unstated procurement parameters         │
│     - Generates actionable explanations for procurement  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│              Deterministic Decision Framework            │
│                                                          │
│  - Negative Evidence Priority (Fatal conflicts override) │
│  - Principled Abstention (INSUFFICIENT_EVIDENCE)         │
│  - Primary vs Alternative vs Multiple Plausible Standards │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│          Grounded Synthesizer & Security Guard           │
│                                                          │
│  - Prompt Injection Sanitization (Data vs Instructions)   │
│  - Grounding Guard: Verifies citations against DB        │
│  - Schema Validation via Pydantic                        │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
  ApplicabilityAssessment + Component Evidence Matrix
```

---

## 2. Core Architectural Principles

### 2.1 Retrieval Similarity $\neq$ Technical Applicability
In Phase 3, dense vectors and BM25 identify candidate standards sharing relevant keywords or concepts. However, high semantic similarity does **not** constitute legal or technical applicability:
- A tender for an *industrial continuous motor* may retrieve a domestic appliance motor standard because both discuss electric motors.
- The Applicability Engine evaluates legal scope boundaries, application domains, and explicit exclusions before certifying applicability.

### 2.2 Component Evidence Matrix (No Opaque Percentages)
The system rejects uncalibrated "AI confidence = 94%" scores. Instead, every candidate standard is accompanied by an inspectable Component Evidence Matrix:
- `scope_match`: `EXACT | PARTIAL | UNCLEAR | CONFLICT`
- `product_match`: `EXACT | CATEGORY | AMBIGUOUS | MISMATCH`
- `parameter_match`: `COMPATIBLE | INCOMPATIBLE | UNCHECKED`
- `application_match`: `COMPATIBLE | INCOMPATIBLE | UNCHECKED`
- `explicit_reference`: Boolean flag indicating direct procurement specification citation
- `exclusion_match`: Boolean flag indicating active exclusion clauses
- `negative_evidence`: List of fatal and warning conflicts
- `evidence_alignment_index`: Normalized deterministic aggregate $[0.0, 1.0]$ based on verified evidence weights, clearly documented as an evidence alignment metric, not a probability.

### 2.3 Strict Priority of Negative Evidence
If a candidate standard has a fatal conflict (e.g. scope explicitly states *"intended exclusively for domestic appliances"* or voltage rating excludes $415\text{ V}$), the candidate is assigned `NOT_APPLICABLE` regardless of whether its semantic retrieval score was 0.99.

### 2.4 Principled Abstention
When technical parameters are missing or scope boundaries cannot be verified from indexed BIS records, the engine explicitly abstains with `INSUFFICIENT_EVIDENCE` or `MULTIPLE_PLAUSIBLE_STANDARDS`. Abstention is treated as a correct, high-integrity system outcome.

---

## 3. Evidence-First Component Specifications

### 3.1 Scope Analyzer (`app.services.applicability.scope_analyzer`)
- Extracts scope text from `IndianStandard.scope` and `Clause` records where `clause_number` starts with `'1'` or contains `'scope'`.
- Detects exclusionary triggers (`"excludes"`, `"not applicable to"`, `"does not cover"`, `"intended exclusively for"`).
- Analyzes domain-specific features (e.g. `IE3`, `PE 100`, `E250`) to establish specific scope alignment.

### 3.2 Product Matcher (`app.services.applicability.product_matcher`)
- Normalizes requirement product names and compares them against standard titles and subject categories.
- Prevents weak keyword overmatching: generic single words (e.g. `"motor"`, `"pipe"`, `"steel"`) yield `CATEGORY` match rather than `EXACT`, forcing parameter and application verification.

### 3.3 Application Matcher (`app.services.applicability.application_matcher`)
- Compares requirement operating environments (`industrial`, `domestic`, `water_supply`, `structural`, `agricultural`, `medical`, `marine`) with candidate domain coverage.
- Flags incompatible environments as fatal conflicts.

### 3.4 Parameter Comparator (`app.services.applicability.parameter_comparator`)
- Extracts structured parameters (`power`, `voltage`, `frequency`, `pressure_pn`, `yield_strength`) from requirement evidence.
- Compares them against verified standard ranges extracted from indexed clause content.
- Never hallucinates standard bounds: if a standard does not define quantitative ranges in indexed clauses, parameter matching status remains `UNCHECKED`.

### 3.5 Missing Information Detector (`app.services.applicability.missing_info_detector`)
- Evaluates requirement completeness based on product category requirements.
- Flags absent engineering parameters (e.g. rated voltage, duty cycle, pressure rating) with impact explanations explaining why the parameter is required for definitive standardization.

---

## 4. Grounded Synthesis & Prompt Security

### 4.1 Grounding Guard (`GroundedVerificationGuard`)
- Validates every generated standard number and clause reference against the persistent database.
- Strips any hallucinated standards or clauses before API responses are serialized.

### 4.2 Prompt Injection Sanitization (`PromptSanitizer`)
- Treats all uploaded tender and procurement text strictly as untrusted DATA.
- Strips system instruction override vectors (e.g. `"ignore previous instructions"`, `"system prompt"`, `"you are now"`).
