# Data Model: Decision Package Schemas

## 1. Pydantic Schemas

Phase 8 exposes strict Pydantic schemas in `app/schemas/intelligence.py` using `ConfigDict(from_attributes=True)`.

### 1.1 `ProcurementDecisionPackageRead`

```python
class ProcurementDecisionPackageRead(BaseModel):
    run: ProcurementIntelligenceRunRead
    executive_summary: ExecutiveSummaryRead
    requirements_summary: List[RequirementRead] = Field(default_factory=list)
    standards_summary: StandardDecisionSummaryRead
    edition_currentness: EditionCurrentnessSummaryRead
    dependencies: DependencySummaryRead
    qco_certification: QcoCertificationSummaryRead
    gaps: GapSummaryRead
    readiness: ProcurementReadinessAssessmentRead
    actions: List[ProcurementReviewActionRead] = Field(default_factory=list)
    checklist: TenderReviewChecklistRead
    clarifications: ClarificationPackageRead
    traceability: TraceabilityReportRead
    evidence_index: EvidenceIndexRead
    limitations: List[SystemLimitationRead] = Field(default_factory=list)
```

### 1.2 `ExecutiveSummaryRead`

```python
class ExecutiveSummaryRead(BaseModel):
    procurement_title: str
    specification_id: int
    requirements_count: int
    standards_count: int
    applicable_standards_count: int
    primary_standard: Optional[str] = None
    alternative_standards: List[str] = Field(default_factory=list)
    currentness_status: str
    critical_gaps_count: int
    high_gaps_count: int
    ambiguities_count: int
    readiness_state: str
    summary_rationale: str
```

### 1.3 `EvidenceIndexRead` & `EvidenceIndexItemRead`

```python
class EvidenceIndexItemRead(BaseModel):
    evidence_id: str
    source_type: str  # TENDER_DOCUMENT, INDIAN_STANDARD, STANDARD_EDITION, CLAUSE, SPECIFICATION_GAP, PROVENANCE_RECORD
    source_url: Optional[str] = None
    source_hash: Optional[str] = None
    provenance_id: Optional[int] = None
    standard_id: Optional[int] = None
    standard_code: Optional[str] = None
    edition_id: Optional[int] = None
    clause_id: Optional[int] = None
    clause_number: Optional[str] = None
    requirement_id: Optional[int] = None
    document_offset: Optional[str] = None
    verified_at: str
    description: str

class EvidenceIndexRead(BaseModel):
    total_evidence_items: int
    entries: List[EvidenceIndexItemRead] = Field(default_factory=list)
```

### 1.4 `TenderReviewChecklistRead` & `ChecklistItemRead`

```python
class ChecklistItemRead(BaseModel):
    item_id: str
    category: str
    label: str
    is_satisfied: bool
    status_text: str
    source_entity: Optional[str] = None
    evidence: Optional[str] = None

class TenderReviewChecklistRead(BaseModel):
    total_items: int
    satisfied_items: int
    unsatisfied_items: int
    items: List[ChecklistItemRead] = Field(default_factory=list)
```

### 1.5 `ClarificationPackageRead` & `ClarificationQuestionRead`

```python
class ClarificationQuestionRead(BaseModel):
    question_number: int
    question_text: str
    reason: str
    evidence_clause: Optional[str] = None
    affected_parameter: Optional[str] = None

class ClarificationPackageRead(BaseModel):
    questions: List[ClarificationQuestionRead] = Field(default_factory=list)
```

---

## 2. Canonical JSON Export

Exporting a decision package emits the entire payload with strict JSON serializability via FastAPI's `ExportJsonRead`:
```json
{
  "export_id": "EXP-RUN-1-1789973200",
  "exported_at": "2026-09-21T06:35:00.000000Z",
  "engine_version": "8.0.0",
  "specification_id": 1,
  "package": { ... }
}
```
