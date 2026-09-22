import React from 'react';
import { ProcurementDecisionPackage } from '../../types/intelligence';
import { exportTraceabilityMatrixToCsv } from '../../utils/exportCsv';
import {
  Printer,
  FileSpreadsheet,
  X,
  CheckCircle2,
} from 'lucide-react';

interface PrintableAuditDossierModalProps {
  pkg: ProcurementDecisionPackage;
  onClose: () => void;
}

export const PrintableAuditDossierModal: React.FC<PrintableAuditDossierModalProps> = ({
  pkg,
  onClose,
}) => {
  const handlePrint = () => {
    window.print();
  };

  const handleExportCsv = () => {
    exportTraceabilityMatrixToCsv(
      pkg.traceability_matrix,
      pkg.executive_summary.tender_reference
    );
  };

  const todayStr = new Date().toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/75 backdrop-blur-sm flex items-start justify-center p-2 sm:p-6 print:p-0 print:bg-white print:static print:overflow-visible">
      <div className="relative w-full max-w-5xl bg-white text-ink-text rounded-2xl shadow-2xl border border-parchment-border overflow-hidden my-4 print:my-0 print:shadow-none print:border-none print:w-full print:max-w-none">
        {/* Action Header (Hidden in Print) */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-3.5 bg-ink-text text-parchment-surface border-b border-ink-dark print:hidden shadow-sm">
          <div className="flex items-center gap-2">
            <Printer size={16} className="text-emerald-400" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider">
              Official Printable Audit Dossier (TEC Review Format)
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportCsv}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-mono transition-colors cursor-pointer"
            >
              <FileSpreadsheet size={13} />
              <span>Export CSV Matrix</span>
            </button>

            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-mono font-bold transition-colors cursor-pointer shadow-xs"
            >
              <Printer size={13} />
              <span>Print / Save as PDF</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors cursor-pointer ml-1"
            >
              <X size={17} />
            </button>
          </div>
        </div>

        {/* Printable Document Body */}
        <div className="p-8 sm:p-12 print:p-6 space-y-8 font-serif text-ink-text bg-[#FCFCFA]">
          {/* Official Letterhead */}
          <div className="border-b-2 border-ink-text pb-6 text-center space-y-2">
            <div className="flex items-center justify-center gap-2 text-xs font-mono tracking-widest uppercase text-ink-muted">
              <span>Government of India</span>
              <span>•</span>
              <span>Central Public Procurement Portal</span>
              <span>•</span>
              <span>Bureau of Indian Standards</span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold font-serif uppercase tracking-tight text-ink-text">
              Statutory Tender Compliance Audit Dossier
            </h1>

            <div className="text-xs font-mono text-ink-muted">
              Issued under Section 16 & Section 29 of the Bureau of Indian Standards Act, 2016
            </div>
          </div>

          {/* Dossier Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-lg bg-parchment-subtle/70 border border-parchment-border text-xs font-mono">
            <div>
              <span className="block text-[10px] text-ink-muted uppercase">TENDER REFERENCE</span>
              <strong className="text-ink-text text-sm">
                {pkg.executive_summary.tender_reference}
              </strong>
            </div>
            <div>
              <span className="block text-[10px] text-ink-muted uppercase">ISSUING ENTITY / PSU</span>
              <strong className="text-ink-text text-sm">
                {pkg.executive_summary.issuing_psu}
              </strong>
            </div>
            <div>
              <span className="block text-[10px] text-ink-muted uppercase">DATE OF AUDIT</span>
              <strong className="text-ink-text text-sm">{todayStr}</strong>
            </div>
            <div>
              <span className="block text-[10px] text-ink-muted uppercase">READINESS VERDICT</span>
              <span className="inline-block px-2 py-0.5 rounded font-bold text-xs bg-amber-100 text-amber-900 border border-amber-300 mt-0.5">
                {pkg.executive_summary.readiness_verdict}
              </span>
            </div>
          </div>

          {/* Cryptographic Integrity Strip */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 px-3 py-2 rounded bg-parchment-subtle border border-parchment-border/60 text-[10px] font-mono text-ink-muted">
            <div className="truncate">
              SHA-256 PACKAGE INTEGRITY HASH: <span className="text-ink-text font-bold">{pkg.package_sha256}</span>
            </div>
            <div className="shrink-0 font-bold text-mineral-blue">
              {pkg.engine_version}
            </div>
          </div>

          {/* Section 1: Statutory Compliance Certification */}
          <div className="space-y-2 text-xs leading-relaxed">
            <h2 className="text-sm font-bold font-serif uppercase tracking-wider text-ink-text border-b border-parchment-border pb-1">
              1. Statutory Authority & Legal Mandate
            </h2>
            <p className="text-ink-text/90 italic">
              "In exercise of the powers conferred by Section 16 of the Bureau of Indian Standards Act, 2016 (11 of 2016), the Central Government has prohibited the manufacture, import, distribution, sale, or public procurement of items covered under mandatory Quality Control Orders unless conforming to the relevant Indian Standard and bearing the Standard Mark (ISI mark) under a license from the Bureau of Indian Standards."
            </p>
            <p className="text-ink-muted text-[11px] font-mono">
              Primary Standard Evaluated: <strong>{pkg.executive_summary.primary_standard_recommended}</strong> | QCO Enforcement Status: <strong>{pkg.executive_summary.qco_enforcement_status}</strong>
            </p>
          </div>

          {/* Section 2: Summary of Pre-Tender Corrigenda */}
          <div className="space-y-3">
            <h2 className="text-sm font-bold font-serif uppercase tracking-wider text-ink-text border-b border-parchment-border pb-1">
              2. Schedule of Recommended Tender Corrigenda & Clause Reconciliations
            </h2>
            <p className="text-xs text-ink-muted">
              The following {pkg.review_actions.length} discrepancies require mandatory rectification prior to tender publication on CPPP / GeM:
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border border-parchment-border">
                <thead>
                  <tr className="bg-parchment-subtle font-mono text-[10px] text-ink-muted uppercase border-b border-parchment-border">
                    <th className="p-2.5 w-16">Item</th>
                    <th className="p-2.5 w-24">Priority</th>
                    <th className="p-2.5 w-44">Tender Section</th>
                    <th className="p-2.5">Non-Compliant Issue & Root Cause</th>
                    <th className="p-2.5">Mandatory Addendum Clause</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-parchment-border text-[11px]">
                  {pkg.review_actions.map((action, idx) => (
                    <tr key={action.id} className="align-top">
                      <td className="p-2.5 font-mono font-bold text-ink-muted">{idx + 1}</td>
                      <td className="p-2.5 font-mono">
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                          action.priority === 'BLOCKING'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}>
                          {action.priority}
                        </span>
                      </td>
                      <td className="p-2.5 font-mono text-ink-muted">{action.affected_section}</td>
                      <td className="p-2.5">
                        <strong className="block text-ink-text font-serif mb-0.5">{action.title}</strong>
                        <p className="text-ink-muted text-[10px]">{action.root_cause}</p>
                      </td>
                      <td className="p-2.5 font-serif italic text-ink-text bg-parchment-subtle/40">
                        {action.recommended_addendum_clause}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 3: Requirement-to-Clause Traceability Schedule */}
          <div className="space-y-3">
            <h2 className="text-sm font-bold font-serif uppercase tracking-wider text-ink-text border-b border-parchment-border pb-1">
              3. Verbatim Traceability & Evidence Verification Schedule
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border border-parchment-border">
                <thead>
                  <tr className="bg-parchment-subtle font-mono text-[10px] text-ink-muted uppercase border-b border-parchment-border">
                    <th className="p-2.5 w-20">Req Code</th>
                    <th className="p-2.5">Tender Stipulation</th>
                    <th className="p-2.5 w-32">Indian Standard</th>
                    <th className="p-2.5 w-32">Clause Ref</th>
                    <th className="p-2.5 w-24">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-parchment-border text-[11px] font-mono">
                  {pkg.traceability_matrix.map((row, idx) => (
                    <tr key={idx} className="align-top">
                      <td className="p-2.5 font-bold text-ink-text">{row.requirement_code}</td>
                      <td className="p-2.5 font-serif text-ink-text">
                        <div>{row.requirement_title}</div>
                        <span className="text-[10px] text-ink-muted font-mono">{row.tender_citation}</span>
                      </td>
                      <td className="p-2.5 text-ink-text">{row.applicable_standard}</td>
                      <td className="p-2.5 text-ink-muted">{row.standard_clause}</td>
                      <td className="p-2.5">
                        <span className="text-emerald-700 font-bold flex items-center gap-1">
                          <CheckCircle2 size={11} /> {row.compliance_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 4: Formal Committee Sign-Off Block */}
          <div className="pt-6 border-t-2 border-ink-text space-y-6">
            <h2 className="text-sm font-bold font-serif uppercase tracking-wider text-ink-text">
              4. Technical Evaluation Committee (TEC) Institutional Sign-Off
            </h2>

            <div className="grid grid-cols-3 gap-6 pt-8 text-center text-xs font-mono">
              <div className="space-y-8">
                <div className="border-b border-ink-text/40 pb-1">
                  <span className="text-[10px] text-ink-muted block uppercase">PREPARED BY</span>
                  <div className="h-8" />
                  <strong className="text-ink-text block">Tendering Authority</strong>
                  <span className="text-[10px] text-ink-muted">Executive Engineer / Dy. Manager</span>
                </div>
                <div className="text-[9px] text-ink-muted">Signature & Date</div>
              </div>

              <div className="space-y-8">
                <div className="border-b border-ink-text/40 pb-1">
                  <span className="text-[10px] text-ink-muted block uppercase">REVIEWED BY</span>
                  <div className="h-8" />
                  <strong className="text-ink-text block">Technical Evaluation Committee</strong>
                  <span className="text-[10px] text-ink-muted">Convener / Chief Technical Examiner</span>
                </div>
                <div className="text-[9px] text-ink-muted">Signature & Date</div>
              </div>

              <div className="space-y-8">
                <div className="border-b border-ink-text/40 pb-1">
                  <span className="text-[10px] text-ink-muted block uppercase">APPROVED BY</span>
                  <div className="h-8" />
                  <strong className="text-ink-text block">Competent Financial Authority</strong>
                  <span className="text-[10px] text-ink-muted">General Manager / HoD Procurement</span>
                </div>
                <div className="text-[9px] text-ink-muted">Signature & Official Seal</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
