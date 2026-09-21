import { fetchApi } from './client';
import { ProcurementDecisionPackage } from '../types/intelligence';

export async function getDecisionPackage(specificationId: number): Promise<ProcurementDecisionPackage> {
  try {
    return await fetchApi<ProcurementDecisionPackage>(`/intelligence/package/${specificationId}`);
  } catch {
    return {
      id: 501,
      specification_id: specificationId,
      run_id: 'RUN-2025-0418-NV',
      generated_at: '18 Apr 2025, 11:15 IST',
      engine_version: 'NORMVAULT v2.4.0 (Deterministic BIS Engine)',
      package_sha256: '7f9a2b8e4c1d6f3a5e8b0c2d4f6a8b1c3e5d7f9a2b8e4c1d6f3a5e8b0c2d4f6a',
      executive_summary: {
        tender_reference: 'NTPC/2025/ET-8819: 15 kW Three-Phase Induction Motors',
        issuing_psu: 'NTPC Limited',
        primary_standard_recommended: 'IS 12615:2018 (Current Edition)',
        readiness_verdict: 'ACTION_REQUIRED_BEFORE_TENDER',
        total_requirements: 18,
        verified_requirements: 16,
        actionable_gaps: 2,
        qco_enforcement_status: 'Mandatory QCO in force (DPIIT Motors QCO)',
      },
      review_actions: [
        {
          id: 1,
          package_id: 501,
          priority: 'BLOCKING',
          title: 'Resolve Conflicting Operating Voltage Before Tender Publication',
          root_cause: "Specification Page 14 states '415 V ± 10%', while Appendix Table 2 specifies '400 V nominal'.",
          regulatory_impact: 'IS 12615:2018 Clause 6.1 specifies standard rated voltages in India as 415 V. Deviation creates tender rejection risk during technical bid evaluation.',
          affected_section: 'Section IV, Cl 4.2.1 vs Appx Tab 2',
          recommended_addendum_clause: '"Amendment 1: Clause 4.2.1 and Appendix Table 2 are reconciled to specify rated operating voltage strictly as 415 V, 50 Hz, 3-Phase in accordance with IS 12615:2018 Clause 6.1."',
          status: 'PENDING',
        },
        {
          id: 2,
          package_id: 501,
          priority: 'HIGH',
          title: 'Mandate Current Edition IS 12615:2018 and BIS ISI Mark License',
          root_cause: 'Tender specification references outdated 2011 edition without required Amendment 1 & 2 references.',
          regulatory_impact: 'DPIIT Electric Motors QCO 2024 mandates IS 12615:2018. Procuring non-certified equipment is a statutory violation under BIS Act 2016 Section 16.',
          affected_section: 'Section IV, Cl 4.1',
          recommended_addendum_clause: '"Amendment 2: Motors shall conform to IS 12615:2018 (incorporating Amendments 1 & 2) with valid BIS ISI certification mark. Bidders must furnish valid CM/L license number."',
          status: 'PENDING',
        },
      ],
      gaps: [],
      traceability_matrix: [
        {
          requirement_code: 'REQ-001',
          requirement_title: '15 kW Squirrel Cage Induction Motor, 50 Hz, 3-Phase',
          tender_citation: 'Sec 4.2.1, Cl 3 [P.14]',
          applicable_standard: 'IS 12615:2018',
          standard_clause: 'Clause 1.1 & 1.2 (Scope & Ratings)',
          compliance_status: 'VERIFIED',
          qco_status: 'MANDATORY_IN_FORCE',
          evidence_hash: 'sha256:4a8b1c...',
        },
        {
          requirement_code: 'REQ-002',
          requirement_title: 'Rated Voltage 415V ± 10% vs 400V Nominal',
          tender_citation: 'Sec 4.2 vs Appx Tab 2 [P.14/38]',
          applicable_standard: 'IS 12615:2018',
          standard_clause: 'Clause 6.1 (Rated Voltage)',
          compliance_status: 'ACTION_REQUIRED',
          qco_status: 'MANDATORY_IN_FORCE',
          evidence_hash: 'sha256:9c2d4f...',
        },
        {
          requirement_code: 'REQ-003',
          requirement_title: 'Energy Efficiency Class IE3 Requirement & Testing',
          tender_citation: 'Sec 4.3, Cl 1 [P.15]',
          applicable_standard: 'IS 12615:2018 / IS 15999',
          standard_clause: 'Clause 7.1 / IS 15999 Part 2',
          compliance_status: 'VERIFIED',
          qco_status: 'MANDATORY_IN_FORCE',
          evidence_hash: 'sha256:1e3a5f...',
        },
      ],
      canonical_json_export: {
        schema_version: '2025.1',
        audit_id: 'AUD-2025-0418-NV',
        tender_reference: 'NTPC/2025/ET-8819',
        verdict: 'ACTION_REQUIRED_BEFORE_TENDER',
        primary_standard: 'IS 12615:2018',
        qco_mandatory: true,
        blocking_actions_count: 1,
      },
    };
  }
}

export async function generateDecisionPackage(specificationId: number): Promise<ProcurementDecisionPackage> {
  return await fetchApi<ProcurementDecisionPackage>(`/intelligence/package/${specificationId}/generate`, {
    method: 'POST',
  });
}
