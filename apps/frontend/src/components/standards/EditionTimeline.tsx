import React, { useState } from 'react';
import { CurrentnessEvaluation } from '../../types/standard';
import { StatusBadge } from '../common/StatusBadge';
import {
  FileDiff,
  ChevronDown,
  ChevronUp,
  Scale
} from 'lucide-react';

interface EditionTimelineProps {
  currentness: CurrentnessEvaluation;
}

export const EditionTimeline: React.FC<EditionTimelineProps> = ({ currentness }) => {
  const [expandedAmendmentId, setExpandedAmendmentId] = useState<number | null>(
    currentness.active_amendments[0]?.id || null
  );

  const toggleAmendment = (id: number) => {
    setExpandedAmendmentId(expandedAmendmentId === id ? null : id);
  };

  return (
    <div className="parchment-card rounded-xl p-6 mb-8 border border-parchment-border shadow-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-parchment-border mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-mineral-light text-mineral-dark border border-mineral-blue/30 font-semibold">
              CHRONOLOGICAL LIFECYCLE & AMENDMENTS
            </span>
          </div>
          <h3 className="text-lg font-bold font-serif text-ink-text">
            Standard Edition & Amendments Timeline
          </h3>
          <p className="text-xs text-ink-muted font-serif">
            Tracking authoritative revisions, superseded editions, and active clause amendments in force.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <StatusBadge status={currentness.is_current ? 'CURRENT' : 'SUPERSEDED'} size="sm" />
          {currentness.qco_edition_match && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-status-indigoBg text-status-indigo border border-status-indigoBorder font-semibold">
              QCO Edition Aligned
            </span>
          )}
        </div>
      </div>

      {/* Editions Timeline Progression */}
      <div className="mb-8">
        <div className="text-[10px] font-mono uppercase text-ink-muted mb-4 font-semibold">
          LIFECYCLE REVISION PROGRESSION
        </div>

        <div className="relative pl-6 border-l-2 border-parchment-border space-y-6 font-mono text-xs">
          {/* Historical / Previous Editions */}
          {currentness.editions_history && currentness.editions_history.length > 0 ? (
            currentness.editions_history.map((ed) => (
              <div key={ed.id} className="relative">
                <span
                  className={`absolute -left-[31px] top-0.5 w-4 h-4 rounded-full border-2 border-parchment-surface ${
                    ed.is_current ? 'bg-status-sage' : 'bg-status-amber'
                  }`}
                />
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className="font-bold text-ink-text font-serif text-sm">
                    Edition {ed.year} {ed.edition_number ? `(Revision ${ed.edition_number})` : ''}
                  </span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold ${
                      ed.is_current
                        ? 'bg-status-sageBg text-status-sage border border-status-sageBorder'
                        : 'bg-status-amberBg text-status-amber border border-status-amberBorder'
                    }`}
                  >
                    {ed.is_current ? 'MANDATED IN FORCE' : 'SUPERSEDED'}
                  </span>
                </div>
                <p className="text-xs text-ink-muted font-serif mt-0.5">
                  {ed.is_current
                    ? 'Current mandatory authoritative edition recognized by the Bureau of Indian Standards and DPIIT Quality Control Orders.'
                    : ed.supersession_reason || 'Superseded by subsequent revisions. Not valid for new procurement tenders.'}
                </p>
              </div>
            ))
          ) : (
            <>
              {/* Fallback default editions */}
              <div className="relative">
                <span className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-status-amber border-2 border-parchment-surface" />
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-ink-text font-serif text-sm">
                    Historical Edition: 2011 (Second Revision)
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-status-amberBg text-status-amber border border-status-amberBorder font-semibold">
                    SUPERSEDED
                  </span>
                </div>
                <p className="text-xs text-ink-muted font-serif">
                  Superseded by Third Revision. Tenders citing this edition risk non-compliance with the BIS Act 2016.
                </p>
              </div>

              <div className="relative">
                <span className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-status-sage border-2 border-parchment-surface" />
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-ink-text font-serif text-sm">
                    Authoritative Edition: {currentness.latest_edition}
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-status-sageBg text-status-sage border border-status-sageBorder font-semibold">
                    MANDATED IN FORCE
                  </span>
                </div>
                <p className="text-xs text-ink-muted font-serif">
                  Current mandatory standard under DPIIT Quality Control Order 2024.
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Incorporated Amendments with Live Diff Inspector */}
      <div className="pt-6 border-t border-parchment-border">
        <div className="flex items-center justify-between mb-4">
          <div className="text-[10px] font-mono uppercase text-ink-muted font-semibold flex items-center gap-1.5">
            <FileDiff size={13} className="text-mineral-blue" />
            <span>INCORPORATED AMENDMENTS ({currentness.active_amendments.length})</span>
          </div>
          <span className="text-[10px] font-mono text-ink-muted">
            Click any amendment to inspect clause diff
          </span>
        </div>

        <div className="space-y-3">
          {currentness.active_amendments.map((amd) => {
            const isExpanded = expandedAmendmentId === amd.id;

            return (
              <div
                key={amd.id}
                className="rounded-lg bg-parchment-surface border border-parchment-border overflow-hidden transition-all shadow-2xs"
              >
                {/* Amendment Header Accordion Trigger */}
                <div
                  onClick={() => toggleAmendment(amd.id)}
                  className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-parchment-subtle/70 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="w-5 h-5 rounded-full bg-mineral-light text-mineral-dark font-mono text-[10px] font-bold flex items-center justify-center border border-mineral-blue/30">
                      {amd.amendment_number}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-ink-text font-mono text-xs">
                          {amd.title || `Amendment No. ${amd.amendment_number}`}
                        </span>
                        <span className="text-[10px] font-mono text-mineral-blue font-semibold">
                          {amd.clause_affected}
                        </span>
                      </div>
                      <span className="text-[11px] text-ink-muted font-serif">
                        {amd.description}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {amd.issued_date && (
                      <span className="text-[10px] font-mono text-ink-muted hidden sm:inline-block">
                        Issued: {amd.issued_date}
                      </span>
                    )}
                    {isExpanded ? <ChevronUp size={14} className="text-ink-muted" /> : <ChevronDown size={14} className="text-ink-muted" />}
                  </div>
                </div>

                {/* Expanded Clause Diff Inspector */}
                {isExpanded && (
                  <div className="p-4 bg-parchment-subtle border-t border-parchment-border space-y-3 text-xs">
                    {amd.clause_impact_summary && (
                      <div className="text-[11px] font-mono text-status-indigo font-semibold flex items-center gap-1.5">
                        <Scale size={12} />
                        <span>Procurement Impact: {amd.clause_impact_summary}</span>
                      </div>
                    )}

                    {/* Side-by-side or stacked diff */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {/* Old Clause Text */}
                      <div className="p-3 rounded-lg bg-status-crimsonBg/30 border border-status-crimsonBorder">
                        <span className="text-[10px] font-mono text-status-crimson font-bold block mb-1 uppercase">
                          − PREVIOUS CLAUSE WORDING:
                        </span>
                        <p className="font-mono text-[11px] text-ink-text leading-relaxed">
                          {amd.old_clause_text || 'Text prior to amendment issuance.'}
                        </p>
                      </div>

                      {/* New Clause Text */}
                      <div className="p-3 rounded-lg bg-status-sageBg/30 border border-status-sageBorder">
                        <span className="text-[10px] font-mono text-status-sage font-bold block mb-1 uppercase">
                          + AMENDED & CURRENT MANDATED TEXT:
                        </span>
                        <p className="font-mono text-[11px] text-ink-text leading-relaxed">
                          {amd.new_clause_text || 'Amended authoritative clause text.'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
