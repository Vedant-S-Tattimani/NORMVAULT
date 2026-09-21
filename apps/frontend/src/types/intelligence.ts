import { SpecificationGap } from './gap';

export interface ProcurementReviewAction {
  id: number;
  package_id: number;
  priority: 'BLOCKING' | 'HIGH' | 'MEDIUM';
  title: string;
  root_cause: string;
  regulatory_impact: string;
  affected_section: string;
  recommended_addendum_clause: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
}

export interface TraceabilityRow {
  requirement_code: string;
  requirement_title: string;
  tender_citation: string;
  applicable_standard: string;
  standard_clause: string;
  compliance_status: 'VERIFIED' | 'ACTION_REQUIRED' | 'AMBIGUOUS' | 'NON_COMPLIANT';
  qco_status: 'MANDATORY_IN_FORCE' | 'EXEMPT' | 'NOT_APPLICABLE';
  evidence_hash?: string;
}

export interface ExecutiveSummary {
  tender_reference: string;
  issuing_psu: string;
  primary_standard_recommended: string;
  readiness_verdict: string;
  total_requirements: number;
  verified_requirements: number;
  actionable_gaps: number;
  qco_enforcement_status: string;
}

export interface ProcurementDecisionPackage {
  id: number;
  specification_id: number;
  run_id: string; // e.g. "RUN-2025-0418-NV"
  generated_at: string;
  engine_version: string;
  package_sha256: string;
  executive_summary: ExecutiveSummary;
  review_actions: ProcurementReviewAction[];
  gaps: SpecificationGap[];
  traceability_matrix: TraceabilityRow[];
  canonical_json_export: Record<string, unknown>;
}
