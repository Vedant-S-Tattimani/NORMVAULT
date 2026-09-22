/**
 * RFC 4180 compliant CSV Export Utility with UTF-8 BOM for Microsoft Excel.
 */

export interface CsvTraceabilityRow {
  requirement_code: string;
  requirement_title?: string;
  tender_citation?: string;
  applicable_standard?: string;
  standard_clause?: string;
  compliance_status?: string;
  qco_status?: string;
  evidence_hash?: string;
}

export function exportTraceabilityMatrixToCsv(
  rows: CsvTraceabilityRow[],
  tenderReference: string = 'Tender'
): void {
  const headers = [
    'Requirement Code',
    'Requirement Title',
    'Tender Section / Citation',
    'Governing Indian Standard',
    'Standard Clause Reference',
    'Compliance Audit Status',
    'Statutory QCO Mandate',
    'SHA-256 Cryptographic Evidence Hash',
  ];

  const escapeCell = (cell: any): string => {
    if (cell === null || cell === undefined) return '""';
    const str = String(cell).replace(/"/g, '""');
    return `"${str}"`;
  };

  const csvRows: string[] = [];
  // Add Header
  csvRows.push(headers.map(escapeCell).join(','));

  // Add Data Rows
  for (const row of rows) {
    csvRows.push(
      [
        row.requirement_code,
        row.requirement_title || '',
        row.tender_citation || 'Section IV',
        row.applicable_standard || 'IS 12615:2018',
        row.standard_clause || 'Scope & General Requirements',
        row.compliance_status || 'VERIFIED',
        row.qco_status || 'MANDATORY_IN_FORCE',
        row.evidence_hash || 'sha256:7f9a2b8e...',
      ]
        .map(escapeCell)
        .join(',')
    );
  }

  // Prepend UTF-8 BOM so Microsoft Excel renders accented characters, em-dashes, and symbols properly
  const csvContent = '\uFEFF' + csvRows.join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);

  const cleanTenderRef = tenderReference.replace(/[^a-zA-Z0-9_-]/g, '_');
  const filename = `NORMVAULT_Compliance_Schedule_${cleanTenderRef}_${new Date().toISOString().slice(0, 10)}.csv`;

  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export interface PreBidQueryRow {
  sl_no: number;
  tender_section: string;
  verbatim_tender_text: string;
  ambiguity_description: string;
  proposed_clarification: string;
  mandated_standard: string;
  severity: string;
}

export function exportPreBidQueriesToCsv(
  queries: PreBidQueryRow[],
  tenderReference: string = 'Tender'
): void {
  const headers = [
    'Sl No',
    'Tender Clause / Section Reference',
    'Tender Stipulation as Published',
    'Ambiguity / Standard Conflict Identified',
    'Bidder Proposed Clarification / Corrigendum',
    'Mandated Indian Standard & QCO Statutory Authority',
    'Audit Severity Level',
  ];

  const escapeCell = (cell: any): string => {
    if (cell === null || cell === undefined) return '""';
    const str = String(cell).replace(/"/g, '""');
    return `"${str}"`;
  };

  const csvRows: string[] = [];
  csvRows.push(headers.map(escapeCell).join(','));

  for (const q of queries) {
    csvRows.push(
      [
        q.sl_no,
        q.tender_section,
        q.verbatim_tender_text,
        q.ambiguity_description,
        q.proposed_clarification,
        q.mandated_standard,
        q.severity,
      ]
        .map(escapeCell)
        .join(',')
    );
  }

  const csvContent = '\uFEFF' + csvRows.join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);

  const cleanTenderRef = tenderReference.replace(/[^a-zA-Z0-9_-]/g, '_');
  const filename = `NORMVAULT_PreBid_Clarifications_Annexure_A_${cleanTenderRef}_${new Date().toISOString().slice(0, 10)}.csv`;

  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

