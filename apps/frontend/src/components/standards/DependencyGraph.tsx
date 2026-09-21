import React, { useState } from 'react';
import { StandardsDependencyGraph, DependencyNode } from '../../types/standard';
import { StatusBadge } from '../common/StatusBadge';
import {
  ArrowRight,
  BookOpen,
  CheckCircle2
} from 'lucide-react';

interface DependencyGraphProps {
  graph: StandardsDependencyGraph;
  onSelectNode?: (nodeId: string) => void;
  onNavigateToStandard?: (standardNumber: string) => void;
}

export const DependencyGraph: React.FC<DependencyGraphProps> = ({
  graph,
  onSelectNode,
  onNavigateToStandard,
}) => {
  const childNodes = graph.nodes.filter((n) => n.type !== 'PRIMARY');
  const [activeNodeId, setActiveNodeId] = useState<string>(
    childNodes[0]?.id || ''
  );

  const selectedNode = childNodes.find((n) => n.id === activeNodeId) || childNodes[0];
  const matchingEdge = graph.edges.find((e) => e.target === selectedNode?.id);

  const handleNodeClick = (node: DependencyNode) => {
    setActiveNodeId(node.id);
    if (onSelectNode) {
      onSelectNode(node.id);
    }
  };

  const getNodeTypeBadge = (type: string) => {
    switch (type) {
      case 'TEST_METHOD':
      case 'MANDATORY_TEST_METHOD':
        return { label: 'MANDATORY TEST METHOD', bg: 'bg-mineral-light text-mineral-dark border-mineral-blue/30' };
      case 'WITHDRAWN_REF':
      case 'SUPERSEDES_WITHDRAWN':
        return { label: 'SUPERSEDED / WITHDRAWN', bg: 'bg-status-crimsonBg text-status-crimson border-status-crimsonBorder' };
      case 'MANDATORY_QCO':
      case 'STATUTORY_MANDATE':
        return { label: 'STATUTORY QCO MANDATE', bg: 'bg-status-indigoBg text-status-indigo border-status-indigoBorder' };
      case 'SAFETY_REQUIREMENT':
      case 'SAFETY_ENCLOSURE':
        return { label: 'SAFETY REQUIREMENT', bg: 'bg-status-amberBg text-status-amber border-status-amberBorder' };
      case 'DIMENSIONS':
      case 'ALLIED_PRODUCT':
        return { label: 'DIMENSIONAL / INTERCHANGEABILITY', bg: 'bg-parchment-subtle text-ink-muted border-parchment-border' };
      default:
        return { label: type.replace(/_/g, ' '), bg: 'bg-parchment-subtle text-ink-muted border-parchment-border' };
    }
  };

  return (
    <div className="parchment-card rounded-xl p-6 mb-8 border border-parchment-border shadow-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-parchment-border mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-mineral-light text-mineral-dark border border-mineral-blue/30 font-semibold">
              NORMATIVE & STATUTORY TOPOLOGY
            </span>
          </div>
          <h3 className="text-lg font-bold font-serif text-ink-text">
            Technical Standards Dependency Graph
          </h3>
          <p className="text-xs text-ink-muted font-serif">
            Interactive network of normative cross-references, mandatory test methods, and statutory mandates linked to this standard.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[10px] font-mono text-ink-muted flex-wrap">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-mineral-blue" />
            <span>Primary Root</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-status-indigo" />
            <span>Statutory QCO</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-status-crimson" />
            <span>Superseded / Withdrawn</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-status-sage" />
            <span>Test Method</span>
          </span>
        </div>
      </div>

      {/* Primary Root Node */}
      <div className="flex justify-center mb-6">
        <div className="max-w-md w-full p-4 rounded-xl bg-parchment-surface border-2 border-mineral-blue shadow-parchment text-center relative">
          <span className="text-[9px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-mineral-blue text-white inline-block mb-1.5">
            PRIMARY STANDARDS ROOT
          </span>
          <h4 className="text-lg font-serif font-bold text-ink-text">
            {graph.primary_standard.standard_number}
          </h4>
          <p className="text-xs text-ink-muted font-serif mt-0.5">
            {graph.primary_standard.title}
          </p>
          <div className="flex items-center justify-center gap-2 mt-2">
            <StatusBadge status={graph.primary_standard.status} size="sm" />
            {graph.primary_standard.is_qco_mandatory && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-status-indigo text-white font-bold">
                DPIIT QCO MANDATORY
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Connector Line */}
      <div className="text-center text-[10px] font-mono text-ink-muted mb-4 uppercase tracking-widest flex items-center justify-center gap-2">
        <span className="h-px w-16 bg-parchment-border" />
        <span>↓ CLICK ANY CONNECTED STANDARD TO INSPECT LINKED CLAUSE ↓</span>
        <span className="h-px w-16 bg-parchment-border" />
      </div>

      {/* Children Dependency Cards (Interactive Selectable) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-6">
        {childNodes.map((node) => {
          const isSelected = selectedNode?.id === node.id;
          const isWithdrawn = node.type === 'WITHDRAWN_REF' || node.status === 'WITHDRAWN';
          const isQco = node.type === 'MANDATORY_QCO';
          const badge = getNodeTypeBadge(node.type);

          return (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node)}
              className={`p-3.5 rounded-lg border text-left transition-all cursor-pointer ${
                isSelected
                  ? 'border-mineral-blue bg-parchment-subtle shadow-md ring-1 ring-mineral-blue'
                  : isWithdrawn
                  ? 'bg-status-crimsonBg/20 border-status-crimsonBorder/70 hover:border-status-crimson'
                  : isQco
                  ? 'bg-status-indigoBg/20 border-status-indigoBorder/70 hover:border-status-indigo'
                  : 'bg-parchment-surface border-parchment-border hover:border-mineral-blue/60'
              }`}
            >
              <div className="flex items-center justify-between gap-1 mb-1">
                <span className={`text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded border ${badge.bg}`}>
                  {badge.label}
                </span>
                {isSelected && (
                  <span className="text-[10px] font-mono text-mineral-blue font-bold flex items-center gap-0.5">
                    <CheckCircle2 size={11} />
                    <span>Active</span>
                  </span>
                )}
              </div>

              <div className="text-sm font-bold font-serif text-ink-text mt-1">
                {node.label}
              </div>

              <div className="text-[11px] text-ink-muted font-sans mt-1 line-clamp-2">
                {node.clause_content || node.description}
              </div>

              {node.referencing_clause && (
                <div className="mt-2 text-[10px] font-mono text-mineral-blue flex items-center gap-1 font-semibold">
                  <BookOpen size={10} />
                  <span>Referenced in {node.referencing_clause}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Linked Clause & Requirement Detail Inspector */}
      {selectedNode && (
        <div className="p-4 rounded-xl bg-parchment-surface border-2 border-parchment-border shadow-xs">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-parchment-border mb-3">
            <div className="flex items-center gap-2">
              <BookOpen size={15} className="text-mineral-blue" />
              <span className="text-xs font-mono font-bold text-ink-text">
                Normative Linkage & Requirement Details
              </span>
            </div>

            {selectedNode.standard_number && onNavigateToStandard && (
              <button
                onClick={() => onNavigateToStandard(selectedNode.standard_number!)}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono bg-mineral-blue hover:bg-mineral-dark text-white font-semibold transition-all active:scale-95"
              >
                <span>View {selectedNode.standard_number} Catalog Page</span>
                <ArrowRight size={12} />
              </button>
            )}
          </div>

          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <span className="text-[10px] font-mono uppercase text-ink-muted block">TARGET STANDARD / MANDATE</span>
                <span className="font-bold text-ink-text font-serif text-sm">{selectedNode.label}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-ink-muted block">REFERENCING CLAUSE IN {graph.primary_standard.standard_number}</span>
                <span className="font-semibold text-mineral-blue font-mono text-xs">
                  {selectedNode.referencing_clause || matchingEdge?.referencing_clause || 'Clause Reference Indexed in Technical Catalog'}
                </span>
              </div>
            </div>

            {/* Exact Clause Content from Authoritative Text */}
            {(selectedNode.clause_content || matchingEdge?.clause_content) && (
              <div className="p-3 rounded-lg bg-parchment-subtle border border-parchment-border">
                <span className="text-[10px] font-mono uppercase text-ink-muted block mb-1 font-semibold">
                  MANDATORY CLAUSE REQUIREMENT TEXT:
                </span>
                <p className="font-serif text-ink-text text-xs leading-relaxed italic">
                  "{selectedNode.clause_content || matchingEdge?.clause_content}"
                </p>
              </div>
            )}

            <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-ink-muted pt-1">
              <div>
                <span className="text-ink-muted">Relationship: </span>
                <span className="text-ink-text font-semibold">
                  {(matchingEdge?.relationship || selectedNode.type).replace(/_/g, ' ')}
                </span>
              </div>
              {selectedNode.procurement_impact && (
                <div>
                  <span className="text-ink-muted">Procurement Impact: </span>
                  <span className="text-status-indigo font-semibold">
                    {selectedNode.procurement_impact.replace(/_/g, ' ')}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
