import React, { useState } from 'react';
import { Requirement } from '../../types/requirement';
import { StatusBadge } from '../common/StatusBadge';
import { ChevronDown, ChevronUp, Copy, Check, Shield, AlertTriangle } from 'lucide-react';
import { copyToClipboard } from '../../utils/clipboard';

interface RequirementCardProps {
  requirement: Requirement;
  onInspectEvidence?: (req: Requirement) => void;
  onCopyText?: (text: string) => void;
}

export const RequirementCard: React.FC<RequirementCardProps> = ({
  requirement,
  onInspectEvidence,
  onCopyText,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await copyToClipboard(requirement.verbatim_excerpt);
    if (onCopyText) {
      onCopyText(requirement.verbatim_excerpt);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="parchment-card rounded-xl p-4 sm:p-5 mb-4 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-parchment-subtle border border-parchment-border text-ink-text">
              {requirement.requirement_code}
            </span>
            <span className="text-xs text-ink-muted">Category: <strong className="text-ink-text">{requirement.category}</strong></span>
            <span className="text-slate-300">•</span>
            <span className="text-xs text-ink-muted">Section: <strong className="text-ink-text">{requirement.section_citation}</strong></span>
            {requirement.has_conflict && (
              <StatusBadge status="ACTION_REQUIRED" size="sm" />
            )}
          </div>
          <h3 className="text-sm sm:text-base font-bold text-ink-text font-serif">
            {requirement.title}
          </h3>
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 text-ink-muted hover:text-ink-text rounded hover:bg-parchment-subtle transition-colors"
        >
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-parchment-border space-y-4">
          {/* Extracted Parameters */}
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-ink-muted mb-2">
              EXTRACTED PARAMETERS
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {requirement.parameters.map((param, i) => (
                <div
                  key={i}
                  className="p-2 rounded-lg bg-parchment-subtle border border-parchment-border"
                >
                  <div className="text-[10px] text-ink-muted font-mono truncate">
                    {param.name}
                  </div>
                  <div className="text-xs font-bold text-ink-text font-mono truncate mt-0.5">
                    {param.value} {param.unit || ''}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Verbatim Excerpt */}
          <div className="bg-parchment-subtle/50 rounded-lg p-3 border border-parchment-border">
            <div className="flex items-center justify-between text-[10px] font-mono text-ink-muted mb-1">
              <span>VERBATIM TENDER EXCERPT</span>
              <span>{requirement.cryptographic_offset}</span>
            </div>
            <p className="text-xs text-ink-text italic font-serif leading-relaxed">
              "{requirement.verbatim_excerpt}"
            </p>
          </div>

          {/* Conflict Alert if any */}
          {requirement.has_conflict && (
            <div className="p-3 rounded-lg bg-status-amberBg border border-status-amberBorder flex items-start gap-2.5">
              <AlertTriangle size={15} className="text-status-amber shrink-0 mt-0.5" />
              <div className="text-xs text-status-amber">
                <strong className="block font-semibold">Tender Ambiguity Detected</strong>
                {requirement.conflict_description}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-2 pt-1">
            {onCopyText && (
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-parchment-border text-ink-text hover:bg-parchment-subtle text-xs font-mono transition-colors"
              >
                {copied ? <Check size={12} className="text-status-sage" /> : <Copy size={12} />}
                <span>{copied ? 'Copied' : 'Copy Excerpt'}</span>
              </button>
            )}
            {onInspectEvidence && (
              <button
                onClick={() => onInspectEvidence(requirement)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-colors"
              >
                <Shield size={12} />
                <span>Inspect Clause Evidence</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
