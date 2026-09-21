import React from 'react';
import { TraceabilityRow } from '../../types/intelligence';
import { StatusBadge } from '../common/StatusBadge';

interface TraceabilityMatrixProps {
  matrix: TraceabilityRow[];
}

export const TraceabilityMatrix: React.FC<TraceabilityMatrixProps> = ({ matrix }) => {
  return (
    <div className="parchment-card rounded-xl p-5 mb-8">
      <div className="flex items-center justify-between pb-3 border-b border-parchment-border mb-4">
        <div>
          <h3 className="text-sm font-bold font-serif text-ink-text">
            End-to-End Requirement Traceability Matrix
          </h3>
          <p className="text-xs text-ink-muted">
            Mapping tender specifications to candidate standards, clauses, and statutory mandates.
          </p>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-parchment-subtle text-ink-muted border border-parchment-border">
          {matrix.length} CLAUSES MAPPED
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-parchment-border text-[10px] text-ink-muted uppercase">
              <th className="py-2.5 px-3">Req Code & Title</th>
              <th className="py-2.5 px-3">Tender Citation</th>
              <th className="py-2.5 px-3">Applicable Standard</th>
              <th className="py-2.5 px-3">Standard Clause</th>
              <th className="py-2.5 px-3">Compliance</th>
              <th className="py-2.5 px-3">Statutory QCO</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-parchment-border/60">
            {matrix.map((row, idx) => (
              <tr key={idx} className="hover:bg-parchment-subtle/40 transition-colors">
                <td className="py-3 px-3">
                  <div className="font-bold text-ink-text">{row.requirement_code}</div>
                  <div className="text-[11px] text-ink-muted font-sans truncate max-w-xs">
                    {row.requirement_title}
                  </div>
                </td>
                <td className="py-3 px-3 text-ink-text">{row.tender_citation}</td>
                <td className="py-3 px-3 font-bold font-serif text-ink-text">
                  {row.applicable_standard}
                </td>
                <td className="py-3 px-3 text-ink-text">{row.standard_clause}</td>
                <td className="py-3 px-3">
                  <StatusBadge status={row.compliance_status} size="sm" />
                </td>
                <td className="py-3 px-3">
                  <StatusBadge status={row.qco_status} size="sm" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
