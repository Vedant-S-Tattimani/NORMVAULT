export type GapType =
  | 'MISSING_STANDARD_REFERENCE'
  | 'SUPERSEDED_STANDARD_CITED'
  | 'CONFLICTING_PARAMETRIC_REQUIREMENT'
  | 'STATUTORY_QCO_NON_COMPLIANCE'
  | 'AMBIGUOUS_TEST_METHOD'
  | 'MISSING_TOLERANCE_SPECIFICATION';

export type GapSeverity = 'BLOCKING' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface SpecificationGap {
  id: number;
  specification_id: number;
  gap_type: GapType;
  severity: GapSeverity;
  title: string;
  tender_section: string;
  tender_excerpt: string;
  standard_reference?: string;
  standard_clause?: string;
  impact_analysis: string;
  recommended_remedy: string;
  status: 'UNRESOLVED' | 'RESOLVED' | 'WAIVED_BY_AUTHORITY';
}

export interface ComplianceReadinessSummary {
  specification_id: number;
  total_requirements_checked: number;
  total_gaps_identified: number;
  blocking_gaps_count: number;
  high_gaps_count: number;
  readiness_state:
    | 'READY_FOR_PROCUREMENT'
    | 'ACTION_REQUIRED_BEFORE_TENDER'
    | 'CRITICAL_AMBIGUITIES_DETECTED';
  qco_statutory_compliance: boolean;
  auditor_signoff_ready: boolean;
}
