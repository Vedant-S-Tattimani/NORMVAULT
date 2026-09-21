# Data Model: Procurement Intelligence Engine

## 1. Domain Entities

Phase 8 introduces two core database models in `app/models/intelligence.py`:
1. `ProcurementIntelligenceRun`
2. `ProcurementReviewAction`

```
┌─────────────────────────────────────────────────────────────┐
│                 ProcurementIntelligenceRun                  │
├─────────────────────────────────────────────────────────────┤
│ id: Integer (PK)                                            │
│ specification_id: Integer (FK -> procurement_specifications)│
│ input_hash: String(64)                                      │
│ engine_version: String(32)                                  │
│ model_version: String(64)                                   │
│ knowledge_base_version: String(64)                          │
│ retrieval_index_version: String(64)                         │
│ status: String(32) [PENDING, COMPLETED, FAILED]             │
│ execution_duration_ms: Float                                │
│ requirements_count: Integer                                 │
│ standards_count: Integer                                    │
│ applicable_count: Integer                                   │
│ possible_count: Integer                                     │
│ not_applicable_count: Integer                               │
│ insufficient_evidence_count: Integer                        │
│ gap_count: Integer                                          │
│ critical_gap_count: Integer                                 │
│ high_gap_count: Integer                                     │
│ readiness_state: String(64)                                 │
│ overall_status: String(64)                                  │
│ configuration: JSON                                         │
│ run_metadata: JSON                                          │
│ created_at: DateTime                                        │
│ updated_at: DateTime                                        │
└──────────────────────────────┬──────────────────────────────┘
                               │ 1:N
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  ProcurementReviewAction                    │
├─────────────────────────────────────────────────────────────┤
│ id: Integer (PK)                                            │
│ run_id: Integer (FK -> procurement_intelligence_runs)       │
│ action_type: ActionType (SQLEnum)                           │
│ priority: ActionPriority (SQLEnum)                          │
│ description: String(512)                                    │
│ reason: Text                                                │
│ suggested_action: Text                                      │
│ source_gap_id: Integer (FK -> specification_gaps)           │
│ affected_requirement_id: Integer (FK -> spec_requirements)  │
│ affected_standard_id: Integer (FK -> indian_standards)      │
│ evidence: JSON                                              │
│ is_resolved: Boolean                                        │
│ resolution_notes: Text                                      │
│ created_at: DateTime                                        │
│ updated_at: DateTime                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Enums

### 2.1 ActionPriority
- `BLOCKING`: Prevents tender finalization; must be resolved by technical authority.
- `HIGH`: Significant risk to objective acceptance, testing, or certification.
- `MEDIUM`: Ambiguity or guideline omission requiring clarification.
- `LOW`: Informational advisory or interface refinement.

### 2.2 ActionType
1. `CLARIFY_REQUIREMENT`
2. `RESOLVE_CONFLICT`
3. `SPECIFY_PARAMETER`
4. `VERIFY_STANDARD_EDITION`
5. `VERIFY_CURRENTNESS`
6. `REVIEW_AMENDMENT`
7. `VERIFY_TEST_METHOD`
8. `VERIFY_SAFETY_REQUIREMENT`
9. `VERIFY_INSTALLATION_REQUIREMENT`
10. `VERIFY_CERTIFICATION`
11. `VERIFY_QCO`
12. `REVIEW_UNCERTAIN_EVIDENCE`

### 2.3 PackageViewType
- `FULL_ANALYSIS`
- `EXECUTIVE_SUMMARY`
- `TECHNICAL_REVIEW`
- `REGULATORY_REVIEW`
- `TRACEABILITY_REPORT`
- `CLARIFICATION_LIST`

---

## 3. Storage Compatibility

All JSON fields utilize SQLAlchemy's generic `JSON` column type rather than PostgreSQL-specific `JSONB`, ensuring seamless operation across both production PostgreSQL/pgvector environments and lightweight SQLite test/embedded deployments.
