import React, { useState, useEffect } from 'react';
import { ProcurementDecisionPackage } from '../types/intelligence';
import { ProcurementSpecification } from '../types/requirement';
import { getDecisionPackage, StakeholderViewType } from '../api/intelligence';
import { PackageHeader } from '../components/decision-package/PackageHeader';
import { ReviewActionsList } from '../components/decision-package/ReviewActionsList';
import { TraceabilityMatrix } from '../components/decision-package/TraceabilityMatrix';
import { JsonExportViewer } from '../components/decision-package/JsonExportViewer';
import { Toast } from '../components/common/Toast';
import {
  Layers,
  FileSpreadsheet,
  Wrench,
  ShieldCheck,
  FileText,
  Scale,
  LucideIcon,
} from 'lucide-react';

interface DecisionPackagePageProps {
  selectedSpecification?: ProcurementSpecification;
}

const STAKEHOLDER_VIEWS: {
  id: StakeholderViewType;
  label: string;
  icon: LucideIcon;
  role: string;
}[] = [
  { id: 'FULL_ANALYSIS', label: 'Full Analysis', icon: Layers, role: 'Comprehensive Master Dossier' },
  { id: 'EXECUTIVE_SUMMARY', label: 'Executive Summary', icon: FileSpreadsheet, role: 'CPO & Tender Committee' },
  { id: 'TECHNICAL_REVIEW', label: 'Technical Review', icon: Wrench, role: 'Lead Technical Engineers' },
  { id: 'REGULATORY_REVIEW', label: 'Regulatory & QCO', icon: ShieldCheck, role: 'Legal & Compliance Officers' },
  { id: 'TRACEABILITY_REPORT', label: 'Audit Traceability', icon: FileText, role: 'Vigilance & Auditors' },
];

export const DecisionPackagePage: React.FC<DecisionPackagePageProps> = ({
  selectedSpecification,
}) => {
  const [decisionPackage, setDecisionPackage] = useState<ProcurementDecisionPackage | null>(null);
  const [activeView, setActiveView] = useState<StakeholderViewType>('FULL_ANALYSIS');
  const [showJsonViewer, setShowJsonViewer] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      const specId = selectedSpecification?.id || 1;
      const data = await getDecisionPackage(specId);
      setDecisionPackage(data);
    }
    load();
  }, [selectedSpecification]);

  if (!decisionPackage) {
    return (
      <div className="max-w-[1500px] mx-auto px-4 py-16 text-center text-xs font-mono text-ink-muted">
        Loading Procurement Decision Package...
      </div>
    );
  }

  // Filter actions based on stakeholder view
  const filteredActions = decisionPackage.review_actions.filter((action) => {
    if (activeView === 'FULL_ANALYSIS') return true;
    if (activeView === 'EXECUTIVE_SUMMARY') return action.priority === 'BLOCKING';
    if (activeView === 'REGULATORY_REVIEW') {
      return (
        action.regulatory_impact?.toLowerCase().includes('qco') ||
        action.regulatory_impact?.toLowerCase().includes('bis') ||
        action.title?.toLowerCase().includes('qco') ||
        action.title?.toLowerCase().includes('certification')
      );
    }
    if (activeView === 'TECHNICAL_REVIEW') {
      return !action.title?.toLowerCase().includes('qco');
    }
    return true;
  });

  return (
    <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Official Package Header */}
      <PackageHeader
        pkg={decisionPackage}
        onExportJson={() => setShowJsonViewer(!showJsonViewer)}
      />

      {/* ADR 0010 Stakeholder Persona View Switcher */}
      <div className="mb-6 parchment-card rounded-xl p-2.5 bg-parchment-surface border border-parchment-border">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 px-2 pb-2 border-b border-parchment-border/50 mb-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono tracking-wider uppercase text-ink-muted">
              STAKEHOLDER PERSPECTIVE (ADR 0010):
            </span>
            <span className="text-xs font-mono font-bold text-mineral-blue">
              {STAKEHOLDER_VIEWS.find((v) => v.id === activeView)?.role}
            </span>
          </div>
          <span className="text-[10px] font-mono text-ink-muted">
            Tailors intelligence metrics and clause evidence to your institutional role
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-1.5">
          {STAKEHOLDER_VIEWS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeView === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono transition-all cursor-pointer text-left ${
                  isActive
                    ? 'bg-ink-text text-parchment-surface font-semibold shadow-xs'
                    : 'bg-parchment-subtle/50 text-ink-muted hover:text-ink-text hover:bg-parchment-subtle border border-parchment-border/40'
                }`}
              >
                <Icon size={14} className={isActive ? 'text-parchment-surface' : 'text-ink-muted'} />
                <div className="truncate">
                  <div className="leading-tight">{tab.label}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Role-Specific Executive Summary Banner (when in EXECUTIVE_SUMMARY view) */}
      {activeView === 'EXECUTIVE_SUMMARY' && (
        <div className="parchment-card rounded-xl p-5 mb-6 border-l-4 border-l-status-crimson">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <FileSpreadsheet size={18} className="text-status-crimson" />
                <h3 className="text-sm font-bold font-serif text-ink-text">
                  Executive Procurement Verdict & Tender Committee Sign-off Brief
                </h3>
              </div>
              <p className="text-xs text-ink-muted font-serif">
                This specification exhibits {decisionPackage.executive_summary.actionable_gaps} actionable gap(s) and requires pre-tender addenda before CPPP/GeM publishing to avoid statutory non-compliance under Section 16 of the BIS Act, 2016.
              </p>
            </div>
            <div className="shrink-0 text-right font-mono">
              <span className="text-[10px] text-ink-muted block uppercase">READINESS STATE</span>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-status-amberBg text-status-amber border border-status-amberBorder">
                {decisionPackage.executive_summary.readiness_verdict}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Role-Specific Regulatory & QCO Banner (when in REGULATORY_REVIEW view) */}
      {activeView === 'REGULATORY_REVIEW' && (
        <div className="parchment-card rounded-xl p-5 mb-6 border-l-4 border-l-mineral-blue bg-blue-50/20">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Scale size={18} className="text-mineral-blue" />
                <h3 className="text-sm font-bold font-serif text-ink-text">
                  Statutory Legal & Quality Control Order (QCO) Compliance Audit
                </h3>
              </div>
              <p className="text-xs text-ink-muted font-serif">
                Direct statutory review verifying compliance with published Ministry Gazette Orders. Procurement of items covered under mandatory QCOs without BIS Standard Mark (ISI license) constitutes a cognizable offense under Section 29 of the BIS Act, 2016.
              </p>
            </div>
            <span className="shrink-0 text-[10px] font-mono font-bold px-2 py-1 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
              MANDATORY QCO IN EFFECT
            </span>
          </div>
        </div>
      )}

      {/* Canonical JSON Viewer (Toggled by Export Canonical JSON) */}
      {showJsonViewer && (
        <JsonExportViewer data={decisionPackage.canonical_json_export} />
      )}

      {/* Pre-Tender Review Actions (Rendered for Full, Executive, Technical, and Regulatory views) */}
      {activeView !== 'TRACEABILITY_REPORT' && (
        <ReviewActionsList
          actions={filteredActions}
          onCopyAddendum={() => setToastMessage('Copied recommended tender addendum clause.')}
        />
      )}

      {/* End-to-End Traceability Matrix (Rendered for Full, Technical, and Traceability views) */}
      {(activeView === 'FULL_ANALYSIS' ||
        activeView === 'TECHNICAL_REVIEW' ||
        activeView === 'TRACEABILITY_REPORT') && (
        <TraceabilityMatrix matrix={decisionPackage.traceability_matrix} />
      )}

      {/* Toast Notification */}
      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage(null)} />
      )}
    </div>
  );
};

