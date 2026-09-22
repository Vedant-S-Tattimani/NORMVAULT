import React, { useState } from 'react';
import { ProcurementDecisionPackage } from '../../types/intelligence';
import { exportPreBidQueriesToCsv, PreBidQueryRow } from '../../utils/exportCsv';
import { copyToClipboard } from '../../utils/clipboard';
import {
  X,
  Copy,
  Check,
  FileSpreadsheet,
  Printer,
  HelpCircle,
  Filter,
  CheckCircle2,
  Building2,
} from 'lucide-react';

interface PreBidClarificationModalProps {
  pkg: ProcurementDecisionPackage;
  onClose: () => void;
}

export const PreBidClarificationModal: React.FC<PreBidClarificationModalProps> = ({
  pkg,
  onClose,
}) => {
  const [severityFilter, setSeverityFilter] = useState<'ALL' | 'BLOCKING' | 'HIGH' | 'MEDIUM'>('ALL');
  const [copied, setCopied] = useState(false);

  // Convert gaps into CPPP / GeM Pro-forma Pre-Bid Clarification Queries
  const queryRows: PreBidQueryRow[] = (pkg.gaps || []).map((gap, index) => ({
    sl_no: index + 1,
    tender_section: gap.tender_section || `Section ${index + 1}`,
    verbatim_tender_text: gap.tender_excerpt || gap.title,
    ambiguity_description: gap.impact_analysis || `${gap.gap_type}: Discrepancy with national standardization norms.`,
    proposed_clarification: gap.recommended_remedy,
    mandated_standard: gap.standard_reference || 'Authoritative BIS Standard / QCO Mandate',
    severity: gap.severity,
  }));

  const filteredRows = queryRows.filter((r) => {
    if (severityFilter === 'ALL') return true;
    return r.severity === severityFilter;
  });

  const handleExportCsv = () => {
    exportPreBidQueriesToCsv(filteredRows, pkg.executive_summary.tender_reference);
  };

  const handleCopyTable = async () => {
    const tableText = [
      `ANNEXURE A — PRE-BID CLARIFICATION QUERIES FOR ${pkg.executive_summary.tender_reference}`,
      `Issuing Authority: ${pkg.executive_summary.issuing_psu || 'Central Procurement Authority'}`,
      `Date: ${new Date().toLocaleDateString('en-IN')}`,
      '',
      'Sl No | Clause Ref | Tender Text as Published | Ambiguity / Conflict | Bidder Proposed Clarification | Mandated Standard',
      '---|---|---|---|---|---',
      ...filteredRows.map(
        (r) =>
          `${r.sl_no} | ${r.tender_section} | "${r.verbatim_tender_text.replace(/\n/g, ' ')}" | "${r.ambiguity_description.replace(/\n/g, ' ')}" | "${r.proposed_clarification.replace(/\n/g, ' ')}" | ${r.mandated_standard}`
      ),
    ].join('\n');

    await copyToClipboard(tableText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-ink-dark/75 backdrop-blur-xs overflow-y-auto animate-fadeIn">
      <div className="bg-parchment-base border border-parchment-border rounded-2xl shadow-2xl w-full max-w-5xl max-h-[92vh] flex flex-col overflow-hidden text-ink-text my-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-parchment-border bg-parchment-surface/90 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-mineral-light text-mineral-dark">
              <HelpCircle size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base sm:text-lg font-bold font-serif text-ink-text">
                  Pre-Bid Clarification Query Schedule (Annexure A)
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold uppercase">
                  CPPP / GeM Pro-Forma
                </span>
              </div>
              <p className="text-xs text-ink-muted">
                Official pro-forma for raising pre-bid technical ambiguities and statutory standard clarifications.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-ink-muted hover:text-ink-text hover:bg-parchment-subtle transition-colors cursor-pointer"
            title="Close modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* Action Toolbar & Filters */}
        <div className="px-6 py-3 bg-parchment-subtle border-b border-parchment-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shrink-0">
          <div className="flex items-center gap-2 text-xs font-mono">
            <Filter size={13} className="text-ink-muted" />
            <span className="text-ink-muted text-[11px] font-semibold">Severity Filter:</span>
            {(['ALL', 'BLOCKING', 'HIGH', 'MEDIUM'] as const).map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-2.5 py-1 rounded border text-[11px] transition-colors cursor-pointer ${
                  severityFilter === sev
                    ? 'bg-ink-text text-parchment-surface border-ink-text font-bold'
                    : 'bg-parchment-surface text-ink-muted border-parchment-border hover:bg-parchment-subtle'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyTable}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-parchment-surface hover:bg-parchment-subtle border border-parchment-border text-ink-text text-xs font-mono transition-colors shadow-xs cursor-pointer"
              title="Copy markdown table to clipboard"
            >
              {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
              <span>{copied ? 'Table Copied!' : 'Copy Query Table'}</span>
            </button>

            <button
              onClick={handleExportCsv}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-mono font-medium transition-colors shadow-xs cursor-pointer"
              title="Export formatted CSV for Microsoft Excel"
            >
              <FileSpreadsheet size={13} />
              <span>Export Annexure A (CSV)</span>
            </button>

            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-mono font-medium transition-colors shadow-xs cursor-pointer"
            >
              <Printer size={13} />
              <span>Print</span>
            </button>
          </div>
        </div>

        {/* Scrollable Pro-Forma Schedule */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
          {/* Institutional Header Banner */}
          <div className="p-4 rounded-xl bg-parchment-surface border border-parchment-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 font-mono text-xs">
            <div className="space-y-0.5">
              <div className="flex items-center gap-1.5 text-[10px] uppercase font-bold text-mineral-blue">
                <Building2 size={12} />
                <span>Issuing Public Authority</span>
              </div>
              <div className="font-bold font-serif text-sm text-ink-text">
                {pkg.executive_summary.issuing_psu || 'National Thermal Power Corporation (NTPC)'}
              </div>
              <div className="text-[11px] text-ink-muted">
                Tender Ref: <strong className="text-ink-text">{pkg.executive_summary.tender_reference}</strong> • Schedule: Annexure-A Technical Queries
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-parchment-subtle border border-parchment-border text-right text-[11px]">
              <div>Portal: <strong className="text-ink-text">GeM / CPPP e-Procure</strong></div>
              <div>Statutory Basis: <strong className="text-status-sage">BIS Act 2016 & QCO</strong></div>
            </div>
          </div>

          {/* Submission Guidelines Note */}
          <div className="p-3.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs font-serif leading-relaxed">
            <strong>Submission Instructions:</strong> Bidders / Technical Evaluation Committees must submit pre-bid queries within the statutory query window in accordance with CVC circular No. 01/01/2021. All modifications accepted by the buyer will be gazetted via an official Pre-Tender Corrigendum Addendum.
          </div>

          {/* Formal Query Table */}
          <div className="overflow-hidden border border-parchment-border rounded-xl shadow-xs">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-parchment-subtle border-b border-parchment-border text-[10px] font-mono uppercase text-ink-muted">
                  <th className="py-2.5 px-3 font-semibold w-12 text-center">Sl</th>
                  <th className="py-2.5 px-3 font-semibold w-28">Tender Clause Ref</th>
                  <th className="py-2.5 px-3 font-semibold w-1/4">Tender Stipulation as Published</th>
                  <th className="py-2.5 px-3 font-semibold w-1/4">Ambiguity / Standard Conflict Raised</th>
                  <th className="py-2.5 px-3 font-semibold w-1/3">Bidder's Proposed Clarification / Corrigendum</th>
                  <th className="py-2.5 px-3 font-semibold w-24">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-parchment-border bg-parchment-surface">
                {filteredRows.map((row) => (
                  <tr key={row.sl_no} className="hover:bg-parchment-subtle/40 transition-colors">
                    <td className="py-3 px-3 font-mono text-center font-bold text-ink-muted align-top">
                      {row.sl_no}
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-mineral-blue align-top">
                      {row.tender_section}
                    </td>
                    <td className="py-3 px-3 font-serif italic text-ink-text align-top leading-relaxed text-[11px]">
                      "{row.verbatim_tender_text}"
                    </td>
                    <td className="py-3 px-3 font-sans text-status-crimson align-top leading-relaxed text-[11px]">
                      {row.ambiguity_description}
                      <div className="mt-1 font-mono text-[10px] text-ink-muted">
                        Mandated: <strong>{row.mandated_standard}</strong>
                      </div>
                    </td>
                    <td className="py-3 px-3 font-serif text-status-sage font-medium align-top leading-relaxed text-[11px] bg-status-sageBg/10">
                      "{row.proposed_clarification}"
                    </td>
                    <td className="py-3 px-3 font-mono text-[10px] align-top">
                      <span
                        className={`px-2 py-0.5 rounded font-bold uppercase ${
                          row.severity === 'BLOCKING'
                            ? 'bg-rose-100 text-rose-800 border border-rose-300'
                            : row.severity === 'HIGH'
                            ? 'bg-amber-100 text-amber-800 border border-amber-300'
                            : 'bg-blue-100 text-blue-800 border border-blue-300'
                        }`}
                      >
                        {row.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-parchment-surface border-t border-parchment-border flex items-center justify-between shrink-0 text-xs">
          <div className="flex items-center gap-1.5 text-ink-muted font-mono text-[11px]">
            <CheckCircle2 size={13} className="text-emerald-600" />
            <span>Format Compliant with CPPP e-Procurement Portal & GeM Pre-Bid Regulations</span>
          </div>

          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded text-xs font-mono border border-parchment-border bg-parchment-surface hover:bg-parchment-subtle text-ink-text cursor-pointer transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
