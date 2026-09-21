import React, { useState } from 'react';
import { ProcurementReviewAction } from '../../types/intelligence';
import { StatusBadge } from '../common/StatusBadge';
import { AlertOctagon, Copy, Check } from 'lucide-react';
import { copyToClipboard } from '../../utils/clipboard';

interface ReviewActionsListProps {
  actions: ProcurementReviewAction[];
  onCopyAddendum?: (text: string) => void;
}

export const ReviewActionsList: React.FC<ReviewActionsListProps> = ({
  actions,
  onCopyAddendum,
}) => {
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const handleCopy = async (id: number, text: string) => {
    await copyToClipboard(text);
    if (onCopyAddendum) {
      onCopyAddendum(text);
    }
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="parchment-card rounded-xl p-5 mb-8">
      <div className="flex items-center justify-between pb-3 border-b border-parchment-border mb-4">
        <div className="flex items-center gap-2">
          <AlertOctagon size={16} className="text-status-crimson" />
          <h3 className="text-sm font-bold font-serif text-ink-text">
            Pre-Tender Review Actions (Blocking & High Priority)
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-status-amberBg text-status-amber border border-status-amberBorder font-semibold">
          {actions.length} ACTIONS IDENTIFIED
        </span>
      </div>

      <div className="space-y-4">
        {actions.map((action) => (
          <div
            key={action.id}
            className="p-4 rounded-lg bg-parchment-surface border border-parchment-border text-xs"
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <StatusBadge status={action.priority} size="sm" />
                <h4 className="font-bold font-serif text-ink-text text-xs sm:text-sm">
                  {action.title}
                </h4>
              </div>

              <button
                onClick={() => handleCopy(action.id, action.recommended_addendum_clause)}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-[11px] font-mono shrink-0 transition-colors shadow-xs"
              >
                {copiedId === action.id ? <Check size={11} className="text-emerald-400" /> : <Copy size={11} />}
                <span>{copiedId === action.id ? 'Copied' : 'Copy Addendum Clause'}</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 my-3 text-[11px] font-mono">
              <div className="p-2.5 rounded bg-parchment-subtle border border-parchment-border">
                <span className="block text-[10px] text-ink-muted uppercase">ROOT CAUSE IN TENDER</span>
                <p className="text-ink-text font-serif mt-0.5">{action.root_cause}</p>
              </div>

              <div className="p-2.5 rounded bg-parchment-subtle border border-parchment-border">
                <span className="block text-[10px] text-ink-muted uppercase">REGULATORY & STANDARDS IMPACT</span>
                <p className="text-ink-text font-serif mt-0.5">{action.regulatory_impact}</p>
              </div>
            </div>

            <div className="p-2.5 rounded bg-parchment-subtle/70 border border-parchment-border text-ink-text font-serif italic">
              <span className="block text-[10px] font-mono uppercase text-ink-muted not-italic mb-1">
                RECOMMENDED TENDER ADDENDUM CLAUSE ({action.affected_section}):
              </span>
              {action.recommended_addendum_clause}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
