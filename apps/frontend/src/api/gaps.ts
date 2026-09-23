import { fetchApi } from './client';
import { SpecificationGap, ComplianceReadinessSummary } from '../types/gap';

export async function getSpecificationGaps(specificationId: number): Promise<SpecificationGap[]> {
  try {
    return await fetchApi<SpecificationGap[]>(`/gaps/specifications/${specificationId}`);
  } catch (err) {
    console.warn(`Could not load gaps for specification ${specificationId}:`, err);
    return [];
  }
}

export async function getComplianceReadiness(specificationId: number): Promise<ComplianceReadinessSummary> {
  try {
    return await fetchApi<ComplianceReadinessSummary>(`/readiness/specifications/${specificationId}`);
  } catch (err) {
    console.warn(`Could not load readiness for specification ${specificationId}:`, err);
    return {
      specification_id: specificationId,
      total_requirements_checked: 0,
      total_gaps_identified: 0,
      blocking_gaps_count: 0,
      high_gaps_count: 0,
      readiness_state: 'ACTION_REQUIRED_BEFORE_TENDER',
      qco_statutory_compliance: false,
      auditor_signoff_ready: false,
    };
  }
}
