export interface IndianStandard {
  id: number;
  standard_number: string; // e.g. "IS 12615"
  title: string;
  year?: number;
  edition?: string;
  status: 'CURRENT' | 'SUPERSEDED' | 'WITHDRAWN' | 'DRAFT' | 'ACTIVE';
  scope_description?: string;
  scope?: string;
  is_qco_mandatory: boolean;
  is_mandatory_qco?: boolean;
  qco_order_reference?: string;
  qco_reference?: string;
  enforcement_date?: string;
  ministry?: string;
  division_code?: string;
  department?: string;
  created_at?: string;
  updated_at?: string;
}

export interface StandardEdition {
  id: number;
  standard_id: number;
  standard_number?: string;
  edition_number: number | string;
  year: number;
  status?: string;
  is_current: boolean;
  reaffirmation_year?: number;
  superseded_date?: string;
  superseded_by_edition_id?: number;
  superseded_by_standard_number?: string;
  supersession_reason?: string;
  supersession_evidence?: string;
  withdrawal_date?: string;
  withdrawal_reason?: string;
  withdrawal_evidence?: string;
  amendments_count?: number;
  scope_summary?: string;
  amendments?: Amendment[];
}

export interface Amendment {
  id: number;
  standard_id: number;
  standard_number?: string;
  amendment_number: number;
  title?: string;
  issued_date?: string;
  issue_date?: string;
  effective_date?: string;
  clause_affected?: string;
  affected_clauses?: string;
  description?: string;
  summary?: string;
  old_clause_text?: string;
  new_clause_text?: string;
  clause_impact_summary?: string;
  is_effective?: boolean;
  text_diff?: string;
}

export interface DependencyNode {
  id: string;
  label: string;
  type: 'PRIMARY' | 'NORMATIVE_REF' | 'TEST_METHOD' | 'DIMENSIONS' | 'SAFETY_ENCLOSURE' | 'WITHDRAWN_REF' | 'MANDATORY_QCO' | 'SAFETY_REQUIREMENT' | 'ALLIED_PRODUCT' | 'INSTALLATION_PRACTICE';
  standard_number?: string;
  standard_id?: number;
  status?: 'CURRENT' | 'SUPERSEDED' | 'WITHDRAWN' | 'DRAFT' | 'ACTIVE' | 'REFERENCED' | string;
  description?: string;
  referencing_clause?: string;
  clause_content?: string;
  reference_semantics?: string;
  procurement_impact?: string;
  test_name?: string;
}

export interface DependencyEdge {
  source: string;
  target: string;
  relationship: string; // e.g. "MANDATORY_TEST_METHOD", "DIMENSIONAL_INTERCHANGEABILITY"
  is_critical: boolean;
  referencing_clause?: string;
  clause_content?: string;
  reference_semantics?: string;
  procurement_impact?: string;
  test_name?: string;
  condition_text?: string;
  target_standard_id?: number;
}

export interface StandardsDependencyGraph {
  primary_standard: IndianStandard;
  nodes: DependencyNode[];
  edges: DependencyEdge[];
}

export interface CurrentnessEvaluation {
  standard_number: string;
  cited_edition?: string;
  latest_edition: string;
  is_current: boolean;
  is_superseded: boolean;
  is_withdrawn: boolean;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'BLOCKING';
  transition_period_expired: boolean;
  active_amendments: Amendment[];
  corrigendum_required: boolean;
  recommended_clause_text?: string;
  qco_edition_match?: boolean;
  qco_edition_mandate?: number | string;
  evidence_summary?: string;
  editions_history?: StandardEdition[];
}

