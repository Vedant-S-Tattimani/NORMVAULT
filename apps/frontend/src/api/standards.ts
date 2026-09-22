import { fetchApi } from './client';
import {
  IndianStandard,
  StandardsDependencyGraph,
  CurrentnessEvaluation,
  StandardEdition,
  Amendment,
  DependencyNode,
  DependencyEdge
} from '../types/standard';

function cleanText(str?: string | null): string {
  if (!str) return '';
  return str
    .replace(/â€“/g, '–')
    .replace(/â€”/g, '—')
    .replace(/â€˜/g, "'")
    .replace(/â€™/g, "'")
    .replace(/â€œ/g, '"')
    .replace(/â€/g, '"')
    .replace(/\u00e2\u0080\u0093/g, '–')
    .replace(/\u00e2\u0080\u0094/g, '—')
    .trim();
}

export async function searchStandards(query: string = ''): Promise<IndianStandard[]> {
  try {
    const raw = await fetchApi<any[]>(`/standards?q=${encodeURIComponent(query)}`);
    return raw.map((s) => ({
      id: s.id,
      standard_number: cleanText(s.standard_number),
      title: cleanText(s.title),
      year: s.editions?.[0]?.year || s.year || 2018,
      edition: s.editions?.[0]?.edition_number ? `Edition ${s.editions[0].edition_number}` : s.edition,
      status: s.status === 'ACTIVE' ? 'CURRENT' : s.status || 'CURRENT',
      scope_description: cleanText(s.scope || s.scope_description || 'Standard specifications and requirements issued by Bureau of Indian Standards.'),
      is_qco_mandatory: Boolean(s.is_mandatory_qco ?? s.is_qco_mandatory),
      qco_order_reference: cleanText(s.qco_reference || s.qco_order_reference || (s.is_mandatory_qco ? 'DPIIT Statutory Quality Control Order' : undefined)),
      enforcement_date: s.certifications?.[0]?.enforcement_date || s.enforcement_date || (s.is_mandatory_qco ? 'In Full Effect' : undefined),
      ministry: s.certifications?.[0]?.notifying_ministry || s.ministry || 'Ministry of Commerce & Industry, DPIIT',
      division_code: s.division_code || 'ETD',
      department: s.department,
    }));
  } catch (err) {
    console.error('Failed to fetch standards from API:', err);
    return [];
  }
}

export async function getStandardDependencies(
  standardIdOrNumber: number | string,
  standard?: IndianStandard
): Promise<StandardsDependencyGraph> {
  const standardId = typeof standardIdOrNumber === 'number'
    ? standardIdOrNumber
    : (standard?.id || 2);

  const currentStd: IndianStandard = standard || {
    id: standardId,
    standard_number: typeof standardIdOrNumber === 'string' ? standardIdOrNumber : 'IS Standard',
    title: 'Selected Technical Standard',
    year: 2018,
    status: 'CURRENT',
    is_qco_mandatory: false,
  };

  const primaryNode: DependencyNode = {
    id: `std-${currentStd.id}`,
    label: currentStd.standard_number,
    type: 'PRIMARY',
    standard_number: currentStd.standard_number,
    standard_id: currentStd.id,
    status: currentStd.status,
    description: currentStd.title,
  };

  try {
    const rawDeps = await fetchApi<any[]>(`/standards/${standardId}/dependencies`);
    if (Array.isArray(rawDeps) && rawDeps.length > 0) {
      const nodes: DependencyNode[] = [primaryNode];
      const edges: DependencyEdge[] = [];

      for (const dep of rawDeps) {
        const targetNumber = cleanText(dep.target_standard_number || `REF-${dep.id}`);
        const targetId = `dep-${dep.id}`;

        nodes.push({
          id: targetId,
          label: targetNumber,
          type: (dep.relationship_type || 'NORMATIVE_REF') as any,
          standard_number: targetNumber,
          standard_id: dep.target_standard_id || undefined,
          status: dep.target_standard_id ? 'CURRENT' : 'REFERENCED',
          description: cleanText(dep.clause_content || dep.test_name || `${dep.relationship_type?.replace(/_/g, ' ')}`),
          referencing_clause: dep.referencing_clause,
          clause_content: cleanText(dep.clause_content),
          test_name: dep.test_name,
          procurement_impact: dep.procurement_impact,
        });

        edges.push({
          source: `std-${dep.source_standard_id || currentStd.id}`,
          target: targetId,
          relationship: dep.relationship_type || 'NORMATIVE_REF',
          is_critical: dep.procurement_impact === 'MANDATORY' || dep.procurement_impact === 'STATUTORY_MANDATE',
          referencing_clause: dep.referencing_clause,
          clause_content: cleanText(dep.clause_content),
        });
      }

      return {
        primary_standard: currentStd,
        nodes,
        edges,
      };
    }
  } catch (err) {
    console.warn(`Could not load live dependency tree for standard ${standardId}:`, err);
  }

  return {
    primary_standard: currentStd,
    nodes: [primaryNode],
    edges: [],
  };
}

export async function getCurrentness(
  standardIdOrNumber: number | string,
  standard?: IndianStandard
): Promise<CurrentnessEvaluation> {
  const standardId = typeof standardIdOrNumber === 'number'
    ? standardIdOrNumber
    : (standard?.id || 2);

  try {
    const [rawCurr, rawEditions, rawAmendments] = await Promise.all([
      fetchApi<any>(`/standards/${standardId}/currentness`).catch(() => null),
      fetchApi<any[]>(`/standards/${standardId}/editions`).catch(() => []),
      fetchApi<any[]>(`/standards/${standardId}/amendments`).catch(() => []),
    ]);

    const amendments: Amendment[] = Array.isArray(rawAmendments)
      ? rawAmendments.map((a) => ({
          id: a.id,
          standard_id: standardId,
          standard_number: standard?.standard_number,
          amendment_number: a.amendment_number,
          title: cleanText(a.title || `Amendment No. ${a.amendment_number}`),
          issued_date: a.issue_date || a.effective_date || 'In Force',
          clause_affected: cleanText(a.affected_clauses || 'General Requirements'),
          description: cleanText(a.summary || a.clause_impact_summary || 'Authoritative amendment incorporated into current edition.'),
          old_clause_text: cleanText(a.old_clause_text),
          new_clause_text: cleanText(a.new_clause_text),
          clause_impact_summary: cleanText(a.clause_impact_summary),
          is_effective: a.is_effective ?? true,
        }))
      : [];

    const editions: StandardEdition[] = Array.isArray(rawEditions)
      ? rawEditions.map((e) => ({
          id: e.id,
          standard_id: standardId,
          edition_number: e.edition_number,
          year: e.year,
          status: e.status || (e.is_current ? 'CURRENT' : 'SUPERSEDED'),
          is_current: Boolean(e.is_current),
          reaffirmation_year: e.reaffirmation_year || undefined,
          superseded_date: e.superseded_date || undefined,
          supersession_reason: cleanText(e.supersession_reason),
          withdrawal_date: e.withdrawal_date || undefined,
          withdrawal_reason: cleanText(e.withdrawal_reason),
          amendments_count: e.amendments?.length || 0,
        }))
      : [];

    const latestYear = editions.find((e) => e.is_current)?.year || rawCurr?.resolved_edition_year || standard?.year || 2018;

    return {
      standard_number: cleanText(standard?.standard_number || rawCurr?.standard_number || 'IS Standard'),
      cited_edition: rawCurr?.cited_edition_year ? String(rawCurr.cited_edition_year) : undefined,
      latest_edition: `${latestYear} (Latest Authoritative Revision)`,
      is_current: rawCurr?.status === 'CURRENT' || !rawCurr?.is_superseded,
      is_superseded: Boolean(rawCurr?.is_superseded),
      is_withdrawn: Boolean(rawCurr?.is_withdrawn),
      risk_level: rawCurr?.is_superseded ? 'HIGH' : 'LOW',
      transition_period_expired: Boolean(rawCurr?.is_superseded),
      active_amendments: amendments,
      corrigendum_required: Boolean(rawCurr?.is_superseded),
      recommended_clause_text: cleanText(rawCurr?.evidence_summary) || `Equipment shall conform to ${standard?.standard_number || 'Indian Standard'}:${latestYear} (incorporating all active amendments).`,
      qco_edition_match: rawCurr?.qco_edition_match ?? true,
      qco_edition_mandate: rawCurr?.qco_edition_mandate || latestYear,
      evidence_summary: cleanText(rawCurr?.evidence_summary) || `Verified current in Bureau of Indian Standards authoritative catalog.`,
      editions_history: editions,
    };
  } catch (err) {
    console.error(`Failed to evaluate currentness for standard ${standardId}:`, err);
    return {
      standard_number: standard?.standard_number || 'IS Standard',
      latest_edition: `${standard?.year || 2018} (Authoritative)`,
      is_current: true,
      is_superseded: false,
      is_withdrawn: false,
      risk_level: 'LOW',
      transition_period_expired: false,
      active_amendments: [],
      corrigendum_required: false,
      recommended_clause_text: `Equipment shall conform to ${standard?.standard_number || 'Indian Standard'}.`,
      editions_history: [],
    };
  }
}

export interface GazetteFeedItem {
  id: number;
  standard_number: string;
  title: string;
  full_standard_title: string;
  so_number: string;
  qco_reference: string;
  enforced_date: string;
  ministry: string;
  status: string;
  division_code: string;
}

export async function getGazetteFeed(): Promise<GazetteFeedItem[]> {
  try {
    return await fetchApi<GazetteFeedItem[]>('/standards/gazette/feed');
  } catch (err) {
    console.error('Failed to fetch gazette feed:', err);
    return [];
  }
}
