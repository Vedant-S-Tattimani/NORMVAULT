import React, { useState } from 'react';
import { ProcurementDecisionPackage } from '../../types/intelligence';
import { copyToClipboard } from '../../utils/clipboard';
import { X, Copy, Check, Download, Printer, ShieldAlert, FileText } from 'lucide-react';

interface CorrigendumModalProps {
  pkg: ProcurementDecisionPackage;
  onClose: () => void;
}

export const CorrigendumModal: React.FC<CorrigendumModalProps> = ({ pkg, onClose }) => {
  const [copied, setCopied] = useState(false);

  const tenderRef = pkg.executive_summary.tender_reference || 'TENDER/2026/TECH-01';
  const issuingPsu = pkg.executive_summary.issuing_psu || 'Central Public Sector Undertaking';
  const currentDate = new Date().toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  const generatePlainTextNotice = () => {
    let notice = `================================================================================\n`;
    notice += `               GOVERNMENT OF INDIA / PUBLIC SECTOR UNDERTAKING\n`;
    notice += `                     CENTRAL PUBLIC PROCUREMENT PORTAL\n`;
    notice += `================================================================================\n\n`;
    notice += `NOTICE INVITING TENDERS - PRE-BID CORRIGENDUM NO. 01\n`;
    notice += `Tender Reference No. : ${tenderRef}\n`;
    notice += `Issuing Authority    : ${issuingPsu}\n`;
    notice += `Date of Issue        : ${currentDate}\n`;
    notice += `System Verification  : NORMVAULT Authoritative Engine (${pkg.package_sha256.substring(0, 16)}...)\n\n`;
    notice += `SUBJECT: PRE-TENDER TECHNICAL RECTIFICATION & MANDATORY BIS STANDARDS ALIGNMENT\n\n`;
    notice += `All prospective bidders are hereby advised that following the automated and technical\n`;
    notice += `statutory review of tender specifications, the competent authority has approved the\n`;
    notice += `following amendments. These corrections are issued in accordance with Section 16 of\n`;
    notice += `the Bureau of Indian Standards (BIS) Act, 2016 and applicable statutory Quality Control\n`;
    notice += `Orders (QCOs).\n\n`;
    notice += `--------------------------------------------------------------------------------\n`;
    notice += `AMENDMENT SCHEDULE (ORIGINAL VS. RECTIFIED SPECIFICATION)\n`;
    notice += `--------------------------------------------------------------------------------\n\n`;

    pkg.review_actions.forEach((act, idx) => {
      notice += `ITEM ${idx + 1}: ${act.title.toUpperCase()}\n`;
      notice += `[1] Affected Section / Clause  : ${act.affected_section}\n`;
      notice += `[2] Original Tender Provision  : ${act.root_cause}\n`;
      notice += `[3] RECTIFIED / AMENDED CLAUSE : \n    ${act.recommended_addendum_clause}\n`;
      notice += `[4] Statutory / Tech Rationale : ${act.regulatory_impact}\n\n`;
    });

    notice += `--------------------------------------------------------------------------------\n`;
    notice += `SPECIAL STATUTORY STIPULATION:\n`;
    notice += `1. Bidders must hold valid BIS License (ISI Mark) under Scheme-I of BIS (Conformity\n`;
    notice += `   Assessment) Regulations, 2018 where mandated by Gazette QCO.\n`;
    notice += `2. All other terms and conditions of the tender specification remain unchanged.\n\n`;
    notice += `BY ORDER OF THE COMPETENT TENDERING AUTHORITY\n`;
    notice += `${issuingPsu}\n`;
    notice += `Digitally verified via NORMVAULT Engine\n`;
    return notice;
  };

  const handleCopyNotice = async () => {
    const text = generatePlainTextNotice();
    await copyToClipboard(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadNotice = () => {
    const text = generatePlainTextNotice();
    const dataStr = 'data:text/plain;charset=utf-8,' + encodeURIComponent(text);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `Corrigendum_No1_${tenderRef.replace(/[^a-zA-Z0-9_-]/g, '_')}.txt`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink-dark/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-parchment-base border border-parchment-border rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 sm:p-5 bg-parchment-surface border-b border-parchment-border flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-mineral-light border border-mineral-blue/30 text-mineral-dark">
              <FileText size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300 uppercase">
                  GeM / CPPP Format
                </span>
                <span className="text-[10px] font-mono text-ink-muted">CORRIGENDUM NO. 1</span>
              </div>
              <h2 className="text-base sm:text-lg font-bold font-serif text-ink-text">
                Official Pre-Tender Corrigendum Notice
              </h2>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-parchment-subtle text-ink-muted hover:text-ink-text transition-colors cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Scrollable Notice Document */}
        <div className="p-5 sm:p-6 overflow-y-auto flex-1 font-serif text-ink-text space-y-6 text-xs sm:text-sm leading-relaxed">
          {/* Official Letterhead */}
          <div className="text-center pb-4 border-b border-parchment-border space-y-1">
            <p className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
              Central Public Procurement Portal (CPPP) & GeM Notice
            </p>
            <h3 className="text-lg font-bold font-serif uppercase tracking-tight text-ink-text">
              {issuingPsu}
            </h3>
            <p className="text-xs font-mono text-ink-muted">
              Tender Ref: <strong className="text-ink-text">{tenderRef}</strong> | Date: {currentDate}
            </p>
          </div>

          {/* Subject & Preamble */}
          <div className="bg-parchment-surface p-3.5 rounded-lg border border-parchment-border space-y-2">
            <p className="font-bold text-ink-text">
              Subject: Corrigendum No. 1 — Pre-Tender Technical Rectification & Standards Alignment
            </p>
            <p className="text-xs text-ink-muted font-sans leading-normal">
              Following pre-tender statutory compliance and technical specification review through the Bureau of Indian Standards (BIS) decision engine, the following rectifications and amendments are hereby published for the information of all prospective bidders.
            </p>
          </div>

          {/* Amendment Schedule Table */}
          <div className="space-y-3">
            <div className="flex items-center gap-1.5 font-bold font-sans text-xs uppercase tracking-wider text-ink-muted">
              <ShieldAlert size={14} className="text-status-amber" />
              <span>Schedule of Amended Clauses ({pkg.review_actions.length} Reconciliations)</span>
            </div>

            <div className="overflow-x-auto border border-parchment-border rounded-lg bg-parchment-surface">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-parchment-subtle border-b border-parchment-border font-mono text-[10px] text-ink-muted uppercase">
                    <th className="p-3 w-12 text-center">Item</th>
                    <th className="p-3 w-40">Tender Citation</th>
                    <th className="p-3">Original Provision vs. Rectified Clause</th>
                    <th className="p-3 w-52">Statutory Justification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-parchment-border text-xs">
                  {pkg.review_actions.map((act, index) => (
                    <tr key={act.id} className="hover:bg-parchment-subtle/50 transition-colors">
                      <td className="p-3 text-center font-mono font-bold text-ink-muted">
                        {index + 1}
                      </td>
                      <td className="p-3 font-mono font-semibold text-mineral-dark">
                        {act.affected_section}
                      </td>
                      <td className="p-3 space-y-2">
                        <div className="p-2 rounded bg-rose-50/60 border border-rose-200/60 text-ink-text">
                          <span className="block text-[10px] font-mono text-status-crimson uppercase font-bold">
                            Original Tender Provision:
                          </span>
                          <span className="text-xs italic">{act.root_cause}</span>
                        </div>
                        <div className="p-2 rounded bg-emerald-50/70 border border-emerald-200/70 text-ink-text">
                          <span className="block text-[10px] font-mono text-emerald-800 uppercase font-bold">
                            Amended Clause Text:
                          </span>
                          <span className="text-xs font-semibold">{act.recommended_addendum_clause}</span>
                        </div>
                      </td>
                      <td className="p-3 text-[11px] font-sans text-ink-muted">
                        <p>{act.regulatory_impact}</p>
                        <span className="inline-block mt-1 text-[10px] font-mono text-status-indigo font-semibold">
                          BIS Act 2016 Sec. 16 Compliant
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Statutory Note */}
          <div className="p-3 rounded-lg bg-amber-50/70 border border-amber-200 text-xs font-sans text-amber-900 space-y-1">
            <p className="font-bold">Mandatory Quality Control Order (QCO) Notification:</p>
            <p>
              In accordance with DPIIT statutory orders, bids offering equipment without valid BIS certification or quoting superseded standard editions shall be deemed non-responsive and summarily rejected.
            </p>
          </div>

          {/* Signoff */}
          <div className="pt-4 border-t border-parchment-border flex flex-col sm:flex-row justify-between gap-4 text-xs font-mono text-ink-muted">
            <div>
              <p className="font-bold text-ink-text">{issuingPsu}</p>
              <p>Technical Evaluation Committee</p>
            </div>
            <div className="sm:text-right">
              <p>Cryptographic Provenance Hash:</p>
              <p className="text-[11px] text-ink-text break-all">{pkg.package_sha256}</p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-parchment-surface border-t border-parchment-border flex flex-wrap items-center justify-between gap-3 shrink-0">
          <div className="text-xs text-ink-muted font-mono">
            {copied ? (
              <span className="text-emerald-700 font-bold flex items-center gap-1">
                <Check size={14} /> Corrigendum notice copied to clipboard!
              </span>
            ) : (
              <span>Ready for GeM / CPPP portal upload</span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyNotice}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-parchment-border hover:bg-parchment-subtle text-ink-text text-xs font-mono transition-colors cursor-pointer"
            >
              {copied ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} />}
              <span>{copied ? 'Copied' : 'Copy Notice Text'}</span>
            </button>

            <button
              onClick={handleDownloadNotice}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-parchment-border hover:bg-parchment-subtle text-ink-text text-xs font-mono transition-colors cursor-pointer"
            >
              <Download size={13} />
              <span>Download Notice (.txt)</span>
            </button>

            <button
              onClick={() => window.print()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-mineral-blue hover:bg-mineral-dark text-white text-xs font-mono font-medium shadow-xs transition-colors cursor-pointer"
            >
              <Printer size={13} />
              <span>Print Official Corrigendum</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
