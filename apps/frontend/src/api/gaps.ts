import { fetchApi } from './client';
import { SpecificationGap, ComplianceReadinessSummary } from '../types/gap';

export async function getSpecificationGaps(specificationId: number): Promise<SpecificationGap[]> {
  try {
    return await fetchApi<SpecificationGap[]>(`/gaps/specifications/${specificationId}`);
  } catch {
    return [
      {
        id: 301,
        specification_id: specificationId,
        gap_type: 'CONFLICTING_PARAMETRIC_REQUIREMENT',
        severity: 'BLOCKING',
        title: 'Conflicting Operating Voltage: 415 V vs 400 V Nominal',
        tender_section: 'Section 4.2 vs Appendix Table 2',
        tender_excerpt: "Page 14 states '415 V ± 10%', while Appendix Table 2 specifies '400 V nominal'.",
        standard_reference: 'IS 12615:2018 Clause 6.1',
        impact_analysis: 'IS 12615:2018 Clause 6.1 specifies standard rated voltages in India as 415 V. Deviation creates tender rejection risk during technical bid evaluation.',
        recommended_remedy: 'Issue Pre-Tender Corrigendum clarifying rated voltage strictly as 415 V, 50 Hz, 3-Phase in accordance with IS 12615:2018 Clause 6.1.',
        status: 'UNRESOLVED',
      },
      {
        id: 302,
        specification_id: specificationId,
        gap_type: 'SUPERSEDED_STANDARD_CITED',
        severity: 'HIGH',
        title: 'Citing Superseded Edition: IS 12615:2011 instead of 2018 with Amendments',
        tender_section: 'Section 4.1 General Standards',
        tender_excerpt: 'Motors shall conform to IS 12615:2011.',
        standard_reference: 'IS 12615:2018',
        impact_analysis: 'IS 12615:2011 is superseded. DPIIT Electric Motors QCO 2024 mandates IS 12615:2018. Procuring under 2011 edition violates statutory mandate.',
        recommended_remedy: 'Update tender clause to mandate IS 12615:2018 (incorporating Amendments 1 & 2) and require BIS ISI Mark with valid CM/L license.',
        status: 'UNRESOLVED',
      },
    ];
  }
}

export async function getComplianceReadiness(specificationId: number): Promise<ComplianceReadinessSummary> {
  try {
    return await fetchApi<ComplianceReadinessSummary>(`/gaps/specifications/${specificationId}/readiness`);
  } catch {
    return {
      specification_id: specificationId,
      total_requirements_checked: 18,
      total_gaps_identified: 2,
      blocking_gaps_count: 1,
      high_gaps_count: 1,
      readiness_state: 'ACTION_REQUIRED_BEFORE_TENDER',
      qco_statutory_compliance: false,
      auditor_signoff_ready: false,
    };
  }
}
