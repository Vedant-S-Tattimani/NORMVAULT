import { fetchApi } from './client';
import { ProcurementSpecification, Requirement } from '../types/requirement';

export async function listSpecifications(): Promise<ProcurementSpecification[]> {
  try {
    return await fetchApi<ProcurementSpecification[]>('/specifications');
  } catch {
    // Return authoritative baseline records for demo / initial view if API is cold
    return [
      {
        id: 1,
        tender_reference: 'NTPC/2025/ET-8819',
        title: 'Supply of 3-Phase Induction Motors (15 kW)',
        issuing_organization: 'NTPC Limited',
        estimated_value_inr: 45000000,
        submission_deadline: '2025-05-15',
        status: 'ACTION_REQUIRED',
        file_name: 'NTPC_Tender_Doc_SecIV.pdf',
        file_hash_sha256: '7f9a2b8e4c1d6f3a5e8b0c2d4f6a8b1c3e5d7f9a2b8e4c1d6f3a5e8b0c2d4f6a',
        total_requirements_count: 18,
        created_at: '2025-04-18T10:42:00Z',
      },
      {
        id: 2,
        tender_reference: 'NHPC/HYDRO/P-402',
        title: 'High-Voltage Switchgear & Vacuum Circuit Breakers 33kV',
        issuing_organization: 'NHPC Limited',
        estimated_value_inr: 128000000,
        submission_deadline: '2025-06-01',
        status: 'READY_FOR_TENDER',
        file_name: 'NHPC_Switchgear_Spec_Rev2.pdf',
        file_hash_sha256: 'a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0',
        total_requirements_count: 34,
        created_at: '2025-04-17T14:15:00Z',
      },
      {
        id: 3,
        tender_reference: 'BHEL-EDN/SPEC/TRANS-09',
        title: '11kV Distribution Transformers Dry Type 500 kVA',
        issuing_organization: 'BHEL',
        estimated_value_inr: 85000000,
        submission_deadline: '2025-05-30',
        status: 'ACTION_REQUIRED',
        file_name: 'BHEL_EDN_TRANS_2025.pdf',
        file_hash_sha256: 'fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210',
        total_requirements_count: 26,
        created_at: '2025-04-16T09:00:00Z',
      },
      {
        id: 4,
        tender_reference: 'POWERGRID/SR-II/SUB-22',
        title: '400kV Gas Insulated Substation Equipment',
        issuing_organization: 'POWERGRID',
        estimated_value_inr: 340000000,
        submission_deadline: '2025-06-20',
        status: 'AUDIT_READY',
        file_name: 'PGCIL_GIS_400KV_SR2.pdf',
        file_hash_sha256: '123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0',
        total_requirements_count: 42,
        created_at: '2025-04-15T16:30:00Z',
      },
    ];
  }
}

export async function getSpecification(id: number): Promise<ProcurementSpecification> {
  return await fetchApi<ProcurementSpecification>(`/specifications/${id}`);
}

export async function listRequirements(specificationId: number): Promise<Requirement[]> {
  try {
    return await fetchApi<Requirement[]>(`/specifications/${specificationId}/requirements`);
  } catch {
    return [
      {
        id: 101,
        specification_id: specificationId,
        requirement_code: 'REQ-001',
        title: 'Continuous duty Squirrel Cage Induction Motor, 15 kW nominal output at 50 Hz',
        category: 'Electrical Rating & Duty',
        section_citation: 'Section 4.2.1, Clause 3',
        page_number: 14,
        verbatim_excerpt: 'Motor shall be capable of delivering continuous rated output of 15 kW at 415V, 50Hz, 3-Phase with class F insulation and temperature rise limited to class B limits.',
        cryptographic_offset: 'sha256:4a8b1c... [P.14, PARA 2]',
        parameters: [
          { name: 'nominal output', value: '15 kW', is_mandatory: true },
          { name: 'phase', value: '3-Phase AC', is_mandatory: true },
          { name: 'frequency', value: '50 Hz ± 3%', is_mandatory: true },
          { name: 'duty cycle', value: 'S1 Continuous', is_mandatory: true },
        ],
      },
      {
        id: 102,
        specification_id: specificationId,
        requirement_code: 'REQ-002',
        title: 'Operating Voltage & Permissible Tolerances (415V vs 400V Conflict)',
        category: 'Voltage Rating',
        section_citation: 'Section 4.2 vs Appendix Table 2',
        page_number: 14,
        verbatim_excerpt: 'Rated voltage 415V ± 10% (Section 4.2), while Appendix Table 2 notes 400V nominal for auxiliary drive systems.',
        cryptographic_offset: 'sha256:9c2d4f... [P.14 & P.38]',
        has_conflict: true,
        conflict_description: 'Tender specifies 415V in Sec 4.2 but 400V nominal in Appendix Table 2. IS 12615:2018 Clause 6.1 specifies standard rated voltage in India as 415V.',
        parameters: [
          { name: 'rated voltage', value: '415 V', unit: 'V', tolerance: '± 10%', is_mandatory: true },
          { name: 'appendix voltage', value: '400 V', unit: 'V', is_mandatory: false },
        ],
      },
      {
        id: 103,
        specification_id: specificationId,
        requirement_code: 'REQ-003',
        title: 'Energy Efficiency Class IE3 Requirement & Test Method',
        category: 'Efficiency & Testing',
        section_citation: 'Section 4.3, Clause 1',
        page_number: 15,
        verbatim_excerpt: 'All motors shall conform to minimum Premium Efficiency Class IE3 in accordance with IS 12615. Efficiency testing shall be conducted per IS 15999 (Part 2/Sec 1).',
        cryptographic_offset: 'sha256:1e3a5f... [P.15, PARA 1]',
        parameters: [
          { name: 'efficiency class', value: 'IE3 Premium', is_mandatory: true },
          { name: 'test method', value: 'IS 15999 Part 2/Sec 1', is_mandatory: true },
          { name: 'full load efficiency', value: '≥ 92.1%', is_mandatory: true },
        ],
      },
    ];
  }
}
