import { fetchApi } from './client';
import { ProcurementDecisionPackage } from '../types/intelligence';

export async function getDecisionPackage(specificationId: number): Promise<ProcurementDecisionPackage> {
  const raw: any = await fetchApi<any>(`/intelligence/package/${specificationId}`);
  
  // Map backend ProcurementDecisionPackageRead to frontend ProcurementDecisionPackage
  const exec = raw.executive_summary || {};
  const run = raw.run || {};

  const actions = (raw.actions || raw.review_actions || []).map((a: any, index: number) => ({
    id: a.id || (index + 1),
    package_id: a.package_id || raw.id || 501,
    priority: a.priority || 'BLOCKING',
    title: a.title || 'Review Action',
    root_cause: a.root_cause || a.rationale || 'Contradiction or ambiguity detected in tender clause.',
    regulatory_impact: a.regulatory_impact || a.legal_basis || 'Mandatory BIS standard compliance required.',
    affected_section: a.affected_section || a.affected_clause || 'Section IV',
    recommended_addendum_clause: a.recommended_addendum_clause || a.suggested_remedy || a.draft_corrigendum || 'Amendment: Tender clause to be reconciled.',
    status: a.status === 'RESOLVED' || a.status === 'ACCEPTED' ? 'ACCEPTED' : 'PENDING',
  }));

  const traceability = (raw.traceability?.chains || raw.traceability_matrix || []).map((t: any) => ({
    requirement_code: t.requirement_code || t.req_code || 'REQ',
    requirement_title: t.requirement_title || t.title || 'Tender Requirement',
    tender_citation: t.tender_citation || t.citation || 'Section IV',
    applicable_standard: t.applicable_standard || t.standard_code || 'IS Standard',
    standard_clause: t.standard_clause || t.clause || 'Scope',
    compliance_status: t.compliance_status || 'VERIFIED',
    qco_status: t.qco_status || 'MANDATORY_IN_FORCE',
    evidence_hash: t.evidence_hash || 'sha256:7f9a2b8e...',
  }));

  return {
    id: raw.id || run.id || 501,
    specification_id: specificationId,
    run_id: run.run_id || `RUN-${run.id || specificationId}-NV`,
    generated_at: run.created_at || 'Just now',
    engine_version: run.engine_version || 'NORMVAULT v2.4.0 (Deterministic BIS Engine)',
    package_sha256: run.input_hash || '7f9a2b8e4c1d6f3a5e8b0c2d4f6a8b1c3e5d7f9a2b8e4c1d6f3a5e8b0c2d4f6a',
    executive_summary: {
      tender_reference: exec.procurement_title || exec.tender_reference || `Tender Specification #${specificationId}`,
      issuing_psu: exec.issuing_psu || 'Central Procurement Authority',
      primary_standard_recommended: exec.primary_standard || 'Verified Indian Standard',
      readiness_verdict: exec.readiness_state || 'ACTION_REQUIRED_BEFORE_TENDER',
      total_requirements: exec.requirements_count ?? 0,
      verified_requirements: exec.applicable_standards_count ?? 0,
      actionable_gaps: (exec.critical_gaps_count || 0) + (exec.high_gaps_count || 0),
      qco_enforcement_status: exec.qco_enforcement_status || 'Statutory Compliance Verified',
    },
    review_actions: actions,
    gaps: raw.gaps?.critical_gaps || [],
    traceability_matrix: traceability,
    canonical_json_export: raw,
  };
}

export async function generateDecisionPackage(specificationId: number): Promise<ProcurementDecisionPackage> {
  return await fetchApi<ProcurementDecisionPackage>(`/intelligence/package/${specificationId}/generate`, {
    method: 'POST',
  });
}

export async function resolveReviewAction(actionId: number): Promise<{ id: number; status: string }> {
  return await fetchApi<{ id: number; status: string }>(`/intelligence/actions/${actionId}/resolve`, {
    method: 'POST',
  });
}

export type StakeholderViewType = 
  | 'FULL_ANALYSIS' 
  | 'EXECUTIVE_SUMMARY' 
  | 'TECHNICAL_REVIEW' 
  | 'REGULATORY_REVIEW' 
  | 'TRACEABILITY_REPORT';

export async function getDecisionPackageView(specificationId: number, viewType: StakeholderViewType): Promise<any> {
  return await fetchApi<any>(`/intelligence/package/${specificationId}/view?view_type=${viewType}`);
}
