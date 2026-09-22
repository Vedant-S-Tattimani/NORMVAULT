import React, { useState } from 'react';
import { IndianStandard } from '../../types/standard';
import { StatusBadge } from '../common/StatusBadge';
import { copyToClipboard } from '../../utils/clipboard';
import {
  Scale,
  Copy,
  Check,
  ArrowRight,
  BookOpen,
  AlertTriangle,
  History
} from 'lucide-react';

interface StandardHeaderCardProps {
  standard: IndianStandard;
  onOpenQcoDrawer?: () => void;
  onOpenSupersessionDiff?: () => void;
  onNavigateToAnalyze?: (standardNumber: string) => void;
}

export const StandardHeaderCard: React.FC<StandardHeaderCardProps> = ({
  standard,
  onOpenQcoDrawer,
  onOpenSupersessionDiff,
  onNavigateToAnalyze,
}) => {
  const [copied, setCopied] = useState(false);

  const getDivisionName = (code?: string) => {
    switch (code?.toUpperCase()) {
      case 'ETD':
        return 'Electrotechnical Division (ETD)';
      case 'CED':
        return 'Civil Engineering Division (CED)';
      case 'MED':
        return 'Mechanical Engineering Division (MED)';
      case 'ITD':
        return 'Information Technology Division (ITD)';
      default:
        return code ? `${code} Division` : 'Standardization Division';
    }
  };

  const handleCopyCitation = async () => {
    const citation = `${standard.standard_number}:${standard.year || 2018} — ${standard.title}`;
    const success = await copyToClipboard(citation);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isCurrent = standard.status === 'CURRENT' || standard.status === 'ACTIVE';

  return (
    <div className="parchment-card rounded-xl p-6 mb-6 shadow-xs border border-parchment-border">
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-parchment-border">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-mineral-light text-mineral-dark border border-mineral-blue/30 font-semibold uppercase">
            {getDivisionName(standard.division_code)}
          </span>
          <StatusBadge status={standard.status} size="sm" />
          {standard.is_qco_mandatory && (
            <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-status-indigoBg text-status-indigo border border-status-indigoBorder font-semibold">
              <Scale size={11} />
              <span>STATUTORY QCO MANDATE</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Copy Citation Button */}
          <button
            onClick={handleCopyCitation}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono bg-parchment-surface hover:bg-parchment-subtle border border-parchment-border text-ink-text transition-all active:scale-95"
            title="Copy standard citation to clipboard"
          >
            {copied ? (
              <>
                <Check size={13} className="text-status-sage" />
                <span className="text-status-sage font-semibold">Citation Copied!</span>
              </>
            ) : (
              <>
                <Copy size={13} className="text-ink-muted" />
                <span>Copy Citation</span>
              </>
            )}
          </button>

          {/* Compare Superseded Standard Button */}
          {onOpenSupersessionDiff && (
            <button
              onClick={onOpenSupersessionDiff}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono bg-parchment-surface hover:bg-parchment-subtle border border-parchment-border text-ink-text transition-all active:scale-95 cursor-pointer"
              title="Compare with superseded standard revisions & technical shifts"
            >
              <History size={13} className="text-mineral-blue" />
              <span>Compare Superseded</span>
            </button>
          )}

          {/* Jump to Analyze Workspace Button */}
          {onNavigateToAnalyze && (
            <button
              onClick={() => onNavigateToAnalyze(standard.standard_number)}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded text-xs font-mono bg-mineral-blue hover:bg-mineral-dark text-white font-semibold shadow-xs transition-all active:scale-95 cursor-pointer"
            >
              <span>Analyze in Workspace</span>
              <ArrowRight size={13} />
            </button>
          )}
        </div>
      </div>

      {/* Main Standard Header */}
      <div className="mt-4">
        <div className="flex items-baseline gap-3 flex-wrap">
          <h2 className="text-2xl sm:text-3xl font-bold font-serif text-ink-text tracking-tight">
            {standard.standard_number}
          </h2>
          {standard.year && (
            <span className="text-sm font-mono text-ink-muted font-normal">
              Edition {standard.year} {standard.edition ? `(${standard.edition})` : ''}
            </span>
          )}
        </div>

        <p className="text-base font-serif font-medium text-ink-text mt-1.5 leading-snug">
          {standard.title}
        </p>

        {/* Scope / Application Summary */}
        <div className="mt-3.5 p-3.5 rounded-lg bg-parchment-subtle/80 border border-parchment-border text-xs text-ink-text leading-relaxed font-sans">
          <div className="flex items-center gap-1.5 text-[10px] font-mono uppercase text-ink-muted mb-1 font-semibold">
            <BookOpen size={12} className="text-mineral-blue" />
            <span>Scope & Application Description</span>
          </div>
          <p className="font-serif text-[13px] text-ink-text">
            {standard.scope_description || 'Specifies technical specifications, tolerance thresholds, and performance criteria issued by the Bureau of Indian Standards.'}
          </p>
        </div>

        {/* Statutory QCO Mandate Callout if Applicable */}
        {standard.is_qco_mandatory && (
          <div className="mt-3.5 p-3.5 rounded-lg bg-status-indigoBg/30 border border-status-indigoBorder text-xs text-ink-text flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-start gap-2.5">
              <Scale size={16} className="text-status-indigo shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-status-indigo block font-sans text-xs">
                  Statutory Mandate: {standard.qco_order_reference || 'DPIIT Quality Control Order'}
                </span>
                <span className="text-[11px] text-ink-muted font-sans block mt-0.5">
                  Enforced by {standard.ministry || 'Ministry of Commerce & Industry, DPIIT'} • Enforcement Date: {standard.enforcement_date || 'In Full Effect'}. Compulsory BIS ISI Mark required for all public procurement.
                </span>
              </div>
            </div>

            {onOpenQcoDrawer && (
              <button
                onClick={onOpenQcoDrawer}
                className="shrink-0 text-xs font-mono text-status-indigo hover:text-indigo-900 underline font-semibold cursor-pointer"
              >
                View Gazette Order →
              </button>
            )}
          </div>
        )}

        {/* Withdrawn / Superseded Warning Callout */}
        {!isCurrent && (
          <div className="mt-3.5 p-3.5 rounded-lg bg-status-crimsonBg/30 border border-status-crimsonBorder text-xs text-ink-text flex items-start gap-2.5">
            <AlertTriangle size={16} className="text-status-crimson shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-status-crimson block font-sans text-xs">
                Withdrawn / Superseded Standard Notice
              </span>
              <span className="text-[11px] text-ink-muted font-sans block mt-0.5">
                This standard has been superseded by newer revisions. Tenders or purchase specifications citing this standard violate GFR 2017 Rule 144(i) and CVC guidelines.
              </span>
              {onOpenSupersessionDiff && (
                <button
                  onClick={onOpenSupersessionDiff}
                  className="mt-2 inline-flex items-center gap-1 text-xs font-mono text-status-crimson hover:underline font-semibold cursor-pointer"
                >
                  <span>Inspect Supersession Shift & Mandatory Corrigendum →</span>
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
