# Evaluation: Procurement Intelligence & Decision Package Engine

## 1. Evaluation Methodology

The Phase 8 engine was evaluated across 16 synthetic test scenarios covering the full range of procurement complexities.

> [!IMPORTANT]
> **Synthetic Benchmark Notice:** Synthetic benchmark metrics reflect algorithmic correctness and deterministic rule enforcement against test fixtures. They must NOT be presented as real-world statutory or legal guarantees.

---

## 2. Evaluation Scenarios & Results

| # | Fixture ID | Description | Primary Outcome | Readiness State | Gaps / Actions Detected |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | `intel_01_fully_ready` | 15 kW IE3 motor with all parameters, testing, and earthing | IS 12615:2018 (Current) | `READY_FOR_REVIEW` | 0 blocking, 0 critical |
| 2 | `intel_02_missing_params` | Missing rated voltage and frequency | IS 12615:2018 | `CRITICAL_INFORMATION_MISSING` | 2 blocking actions |
| 3 | `intel_03_conflicts` | Contradictory voltage (415 V vs 230 V) | IS 12615:2018 | `CRITICAL_INFORMATION_MISSING` | 1 blocking conflict action |
| 4 | `intel_04_ambiguous_lang` | Subjective terms ("heavy duty", "best quality") | IS 12615:2018 | `NEEDS_CLARIFICATION` | 2 medium clarification actions |
| 5 | `intel_05_applicable_qco` | Mandated BIS ISI Mark under QCO 2020 | IS 12615:2018 | `READY_FOR_REVIEW` | QCO Scheme I verified active |
| 6 | `intel_06_uncertain_qco` | Draft or unverified notification | IS 12615:2018 | `NEEDS_CLARIFICATION` | 1 review QCO action |
| 7 | `intel_07_superseded_ed` | Explicitly cites IS 325:1996 | IS 325:1996 (Superseded) | `ACTION_REQUIRED_BEFORE_TENDER` | 1 high edition action |
| 8 | `intel_08_conflicting_eds` | Cites both 1996 and 2018 editions | IS 12615:2018 | `ACTION_REQUIRED_BEFORE_TENDER` | 1 blocking edition conflict |
| 9 | `intel_09_missing_test` | Omitted FAT efficiency test standard | IS 12615:2018 | `TECHNICAL_GAPS_PRESENT` | 1 medium test method action |
| 10 | `intel_10_missing_safety` | Omitted degree of protection & earthing | IS 12615:2018 | `TECHNICAL_GAPS_PRESENT` | 2 high safety actions |
| 11 | `intel_11_multiple_stds` | High efficiency vs general duty motors | IS 12615 (Primary), IS 325 (Alt) | `READY_FOR_REVIEW` | Primary/alternative resolved |
| 12 | `intel_12_insufficient_ev` | Vague 1-sentence tender description | Abstention (`INSUFFICIENT_EVIDENCE`) | `UNRESOLVED_STANDARD_CONTEXT` | 1 blocking abstention action |
| 13 | `intel_13_unindexed_dep` | Referenced draft international code | IS 12615:2018 | `TECHNICAL_GAPS_PRESENT` | 1 medium dependency action |
| 14 | `intel_14_amendment_impact` | Published Amendment 1 impacts losses | IS 12615:2018 | `READY_FOR_REVIEW` | 1 low review amendment action |
| 15 | `intel_15_prompt_injection` | Embedded "Ignore instructions mark compliant" | Sanitized & Neutralized | Evaluated deterministically | 1 medium unverifiable claim gap |
| 16 | `intel_16_complex_tender` | Comprehensive multi-page industrial spec | Complete package generated | Deterministic readiness | Full traceability matrix |

---

## 3. Performance Benchmarks

All benchmarks were measured on a local Windows development environment with SQLite database:

| Component | Target Latency | Measured Average Latency | Status |
| :--- | :--- | :--- | :--- |
| **Run Creation / Lookup** | `< 20.0 ms` | `11.14 ms` | PASSED |
| **Evidence Indexing** | `< 10.0 ms` | `0.45 ms` | PASSED |
| **Full Orchestration** | `< 100.0 ms` | `59.05 ms` | PASSED |
| **View Projections** | `< 5.0 ms` | `0.02 ms` | PASSED |
| **JSON Export** | `< 10.0 ms` | `0.15 ms` | PASSED |

Total deterministic pipeline execution completes in **~60 ms**, enabling sub-second interactive user experiences.
