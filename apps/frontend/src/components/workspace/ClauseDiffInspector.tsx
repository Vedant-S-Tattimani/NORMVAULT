import React, { useState } from 'react';
import { GitCompare, Copy, Check, FileCode } from 'lucide-react';
import { copyToClipboard } from '../../utils/clipboard';

interface ClauseDiffInspectorProps {
  tenderClauseText?: string;
  standardClauseText?: string;
  corrigendumClauseText?: string;
  onCopyCorrigendum?: (text: string) => void;
}

export const ClauseDiffInspector: React.FC<ClauseDiffInspectorProps> = ({
  tenderClauseText = "Motor shall be rated for 415V ± 10%, 50Hz, 3-Phase (Section 4.2), but auxiliary drive motors may operate on 400V nominal (Appendix Table 2). Motors shall conform to IS 325.",
  standardClauseText = "IS 12615:2018 Clause 6.1: Standard rated voltage shall be 415 V at 50 Hz. Single-speed squirrel cage induction motors shall comply with IE3 efficiency limits tested per IS 15999.",
  corrigendumClauseText = '"Amendment 1: Clause 4.2.1 and Appendix Table 2 are reconciled to specify rated operating voltage strictly as 415 V, 50 Hz, 3-Phase in accordance with IS 12615:2018 Clause 6.1."',
  onCopyCorrigendum,
}) => {
  const [viewMode, setViewMode] = useState<'side-by-side' | 'unified'>('side-by-side');
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await copyToClipboard(corrigendumClauseText);
    if (onCopyCorrigendum) {
      onCopyCorrigendum(corrigendumClauseText);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="parchment-card rounded-xl p-5 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-parchment-border">
        <div className="flex items-center gap-2">
          <GitCompare size={16} className="text-mineral-blue" />
          <h3 className="text-sm font-bold font-serif text-ink-text">
            Clause Reconciliation & Diff Inspector
          </h3>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-parchment-subtle text-ink-muted border border-parchment-border">
            DETERMINISTIC DIFF
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded border border-parchment-border overflow-hidden text-xs font-mono">
            <button
              onClick={() => setViewMode('side-by-side')}
              className={`px-2.5 py-1 ${
                viewMode === 'side-by-side'
                  ? 'bg-ink-text text-parchment-surface font-semibold'
                  : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle'
              }`}
            >
              Side-by-Side
            </button>
            <button
              onClick={() => setViewMode('unified')}
              className={`px-2.5 py-1 ${
                viewMode === 'unified'
                  ? 'bg-ink-text text-parchment-surface font-semibold'
                  : 'bg-parchment-surface text-ink-muted hover:bg-parchment-subtle'
              }`}
            >
              Unified
            </button>
          </div>
        </div>
      </div>

      {/* Comparison View */}
      {viewMode === 'side-by-side' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 font-mono text-xs">
          {/* Tender Specification Side */}
          <div className="rounded-lg bg-status-crimsonBg/30 border border-status-crimsonBorder/70 p-3.5">
            <div className="flex items-center justify-between text-[10px] text-status-crimson font-bold uppercase mb-2">
              <span>TENDER SPECIFICATION (CONFLICTING)</span>
              <span>PAGE 14 / TAB 2</span>
            </div>
            <p className="text-ink-text font-serif text-xs leading-relaxed">
              {tenderClauseText}
            </p>
            <div className="mt-3 text-[11px] text-status-crimson font-mono">
              - 400V nominal in Appendix Table 2 conflicts with Section 4.2
              <br />
              - IS 325 is withdrawn by BIS
            </div>
          </div>

          {/* Authoritative Indian Standard Side */}
          <div className="rounded-lg bg-status-sageBg/30 border border-status-sageBorder/70 p-3.5">
            <div className="flex items-center justify-between text-[10px] text-status-sage font-bold uppercase mb-2">
              <span>AUTHORITATIVE BIS STANDARD (MANDATED)</span>
              <span>IS 12615:2018</span>
            </div>
            <p className="text-ink-text font-serif text-xs leading-relaxed">
              {standardClauseText}
            </p>
            <div className="mt-3 text-[11px] text-status-sage font-mono">
              + 415 V standard rated voltage
              <br />
              + DPIIT Electric Motors QCO 2024 mandatory
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-lg bg-parchment-subtle border border-parchment-border p-4 font-mono text-xs mb-4 space-y-1">
          <div className="text-status-crimson bg-status-crimsonBg/50 p-1.5 rounded">
            - [TENDER SEC 4.2 / TAB 2]: {tenderClauseText}
          </div>
          <div className="text-status-sage bg-status-sageBg/50 p-1.5 rounded">
            + [IS 12615:2018 CL 6.1]: {standardClauseText}
          </div>
        </div>
      )}

      {/* Recommended Corrigendum Clause */}
      <div className="rounded-lg bg-parchment-subtle p-3.5 border border-parchment-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <FileCode size={16} className="text-mineral-blue shrink-0 mt-0.5" />
          <div>
            <div className="text-[10px] font-mono uppercase text-ink-muted font-bold">
              RECOMMENDED PRE-TENDER CORRIGENDUM ADDENDUM CLAUSE
            </div>
            <p className="text-xs font-serif text-ink-text italic mt-0.5">
              {corrigendumClauseText}
            </p>
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-mono shrink-0 transition-colors shadow-xs"
        >
          {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
          <span>{copied ? 'Copied' : 'Copy Addendum Text'}</span>
        </button>
      </div>
    </div>
  );
};
