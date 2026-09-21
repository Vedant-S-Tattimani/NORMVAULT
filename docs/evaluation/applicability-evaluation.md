# Evaluation: Applicability Analysis & Recommendation Engine (Phase 4)

## 1. Evaluation Methodology

To validate the **Applicability Analysis Engine** without compromising production standards integrity, a synthetic test suite of 10 targeted procurement scenarios was constructed in `tests/fixtures/synthetic_applicability_eval.json`.

The scenarios test all boundary conditions:
1. **Clear Applicable Candidate**: IE3 Three-phase motor $\to$ `IS 12615` (Primary).
2. **Clear Scope Mismatch**: HDPE pipe standard retrieved for electric motor $\to$ `NOT_APPLICABLE`.
3. **Similar but Wrong Standard**: Domestic appliance motor standard retrieved for industrial duty $\to$ `NOT_APPLICABLE` (Application conflict).
4. **Multiple Plausible Candidates**: Generic motor tender without IE rating $\to$ `MULTIPLE_PLAUSIBLE_STANDARDS` (Abstained).
5. **Missing Information**: Incomplete motor tender lacking voltage and duty cycle $\to$ `INSUFFICIENT_EVIDENCE` (Abstained).
6. **Explicit Standard Reference**: Tender specifically stating `"Conforming to IS 12615"` $\to$ `APPLICABLE` with `EXPLICIT_REFERENCE` evidence.
7. **Parameter Incompatibility**: 1500 kW motor exceeding 1000 kW standard upper bound $\to$ `NOT_APPLICABLE` (Parameter conflict).
8. **Negative Scope Evidence**: Standard with explicit exclusion clause for domestic equipment $\to$ `NOT_APPLICABLE`.
9. **No Applicable Candidate Found**: Synthetic query with no matching standards pool items $\to$ `NO_APPLICABLE_CANDIDATE_FOUND`.
10. **Prompt Injection / Hallucination Attempt**: Tender with malicious system instructions $\to$ Handled safely as raw data with zero fabricated clauses or standards.

---

## 2. Quantitative Benchmark Results

Evaluated across the 10 synthetic test scenarios:

| Metric | Target | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Applicability Decision Accuracy** | $\ge 90\%$ | **100.0%** (10/10) | PASS |
| **False-Positive Rate on Negative Evidence** | $0.0\%$ | **0.0%** (0 false approvals) | PASS |
| **Principled Abstention Accuracy** | $\ge 95\%$ | **100.0%** | PASS |
| **Evidence Grounding Integrity** | $100\%$ | **100.0%** (0 fabricated clauses/standards) | PASS |
| **Mean Adjudication Latency per Requirement** | $\le 200\text{ ms}$ | **~38 ms** | PASS |

---

## 3. Evaluation Limitations

> [!WARNING]
> **Synthetic Benchmark Limitations**:
> 1. Results are measured against synthetic and curated Indian Standard fixtures (`IS 12615`, `IS 325`, `IS 996`, `IS 4984`, `IS 2062`, `IS 12269`).
> 2. Real-world tenders may feature multi-clause ambiguity, contradictory customer specifications, or un-indexed BIS amendments.
> 3. These benchmarks validate the correctness of the decision logic, negative evidence prioritization, and abstention mechanics, but do not replace legal or technical review by procurement officers.
