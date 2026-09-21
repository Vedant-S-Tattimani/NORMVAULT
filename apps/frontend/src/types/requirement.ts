export interface ProcurementSpecification {
  id: number;
  tender_reference: string;
  title: string;
  issuing_organization: string; // e.g. "NTPC", "NHPC", "BHEL"
  estimated_value_inr?: number;
  submission_deadline?: string;
  status: 'DRAFT' | 'ANALYZED' | 'ACTION_REQUIRED' | 'READY_FOR_TENDER' | 'AUDIT_READY';
  file_name?: string;
  file_hash_sha256?: string;
  total_requirements_count?: number;
  created_at: string;
  updated_at?: string;
}

export interface ParameterExtraction {
  name: string;
  value: string;
  unit?: string;
  tolerance?: string;
  is_mandatory: boolean;
}

export interface Requirement {
  id: number;
  specification_id: number;
  requirement_code: string; // e.g. "REQ-001"
  title: string;
  category: string; // e.g. "Electrical Rating & Duty", "Mechanical Enclosure"
  section_citation: string; // e.g. "Section 4.2.1, Clause 3"
  page_number?: number;
  verbatim_excerpt: string;
  cryptographic_offset?: string;
  parameters: ParameterExtraction[];
  has_conflict?: boolean;
  conflict_description?: string;
}

export interface EvidenceSignal {
  category: string; // e.g. "Scope Match", "Product Match", "Voltage Rating", "Duty Cycle"
  citation: string; // e.g. "IS 12615 Clause 1.1"
  tender_value: string;
  standard_clause_value: string;
  is_matched: boolean;
  weight: number;
}

export interface ApplicabilityAssessment {
  id: number;
  specification_id: number;
  requirement_id?: number;
  standard_number: string;
  standard_title: string;
  verdict: 'APPLICABLE' | 'NOT_APPLICABLE' | 'CONDITIONAL' | 'REVIEW_REQUIRED';
  confidence_score: number;
  determination_rationale: string;
  evidence_matrix: EvidenceSignal[];
  is_mandated_by_qco: boolean;
  superseded_warning?: string;
}
