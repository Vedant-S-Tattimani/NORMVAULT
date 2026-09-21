import React from 'react';
import { ApplicabilityAssessment } from '../../types/requirement';
import { StatusBadge } from '../common/StatusBadge';
import { Check, X, Shield, RefreshCw } from 'lucide-react';

interface ApplicabilityMatrixProps {
  assessment: ApplicabilityAssessment;
  onReevaluate?: () => void;
}

export const ApplicabilityMatrix: React.FC<ApplicabilityMatrixProps> = ({
  assessment,
  onReevaluate,
}) => {
  return (
    <div className="parchment-card rounded-xl p-5 mb-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-4 pb-4 border-b border-parchment-border">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-base font-bold font-serif text-ink-text">
              {assessment.standard_number}
            </span>
            <StatusBadge status={assessment.verdict} size="sm" />
            {assessment.is_mandated_by_qco && (
              <StatusBadge status="QCO_MANDATORY" size="sm" />
            )}
          </div>
          <div className="text-xs text-ink-muted font-serif">
            {assessment.standard_title}
          </div>
        </div>

        {onReevaluate && (
          <button
            onClick={onReevaluate}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-parchment-border text-ink-text hover:bg-parchment-subtle text-xs font-mono transition-colors"
            title="Re-run deterministic applicability evaluation"
          >
            <RefreshCw size={12} />
            <span>Re-evaluate</span>
          </button>
        )}
      </div>

      {/* Rationale */}
      <div className="bg-parchment-subtle/60 rounded-lg p-3 border border-parchment-border mb-4">
        <div className="text-[10px] font-mono uppercase text-ink-muted mb-1 flex items-center gap-1">
          <Shield size={11} className="text-mineral-blue" />
          <span>DETERMINATION RATIONALE</span>
        </div>
        <p className="text-xs text-ink-text font-serif leading-relaxed">
          {assessment.determination_rationale}
        </p>
      </div>

      {/* 8-Point Evidence Checklist */}
      <div>
        <div className="flex items-center justify-between text-[10px] font-mono text-ink-muted uppercase mb-2">
          <span>DETERMINISTIC EVIDENCE MATRIX</span>
          <span>{assessment.evidence_matrix.length} Criteria Evaluated</span>
        </div>

        <div className="space-y-2">
          {assessment.evidence_matrix.map((signal, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-2.5 rounded-lg bg-parchment-surface border border-parchment-border text-xs"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                    signal.is_matched
                      ? 'bg-status-sageBg text-status-sage'
                      : 'bg-status-crimsonBg text-status-crimson'
                  }`}
                >
                  {signal.is_matched ? <Check size={12} /> : <X size={12} />}
                </div>
                <div className="min-w-0">
                  <div className="font-semibold text-ink-text font-serif truncate">
                    {signal.category}
                  </div>
                  <div className="text-[11px] text-ink-muted font-mono truncate">
                    Tender: <span className="text-ink-text">{signal.tender_value}</span> • Ref: {signal.citation}
                  </div>
                </div>
              </div>

              <div className="shrink-0 ml-3">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                    signal.is_matched
                      ? 'bg-status-sageBg text-status-sage border border-status-sageBorder'
                      : 'bg-status-crimsonBg text-status-crimson border border-status-crimsonBorder'
                  }`}
                >
                  {signal.is_matched ? 'MATCHED' : 'UNMATCHED'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
