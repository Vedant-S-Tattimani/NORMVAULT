import React, { useState, useEffect } from 'react';
import { ProcurementSpecification, Requirement, ApplicabilityAssessment } from '../types/requirement';
import { SpecificationGap } from '../types/gap';
import { listSpecifications, listRequirements } from '../api/specifications';
import { getApplicabilityAssessments } from '../api/applicability';
import { getSpecificationGaps } from '../api/gaps';
import { PipelineStepper, PipelineStage } from '../components/workspace/PipelineStepper';
import { RequirementCard } from '../components/workspace/RequirementCard';
import { ApplicabilityMatrix } from '../components/workspace/ApplicabilityMatrix';
import { ClauseDiffInspector } from '../components/workspace/ClauseDiffInspector';
import { EvidenceDrawer } from '../components/workspace/EvidenceDrawer';
import { StatusBadge } from '../components/common/StatusBadge';
import { Toast } from '../components/common/Toast';
import { copyToClipboard } from '../utils/clipboard';
import { Upload, ArrowRight, AlertOctagon, Copy, Check, FileCode } from 'lucide-react';

interface AnalyzePageProps {
  selectedSpecification?: ProcurementSpecification;
  onNavigateToDecisionPackage: () => void;
}

export const AnalyzePage: React.FC<AnalyzePageProps> = ({
  selectedSpecification,
  onNavigateToDecisionPackage,
}) => {
  const [specifications, setSpecifications] = useState<ProcurementSpecification[]>([]);
  const [currentSpec, setCurrentSpec] = useState<ProcurementSpecification | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [assessments, setAssessments] = useState<ApplicabilityAssessment[]>([]);
  const [gaps, setGaps] = useState<SpecificationGap[]>([]);
  const [activeStage, setActiveStage] = useState(3);
  const [inspectingReq, setInspectingReq] = useState<Requirement | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [copiedGapId, setCopiedGapId] = useState<number | null>(null);

  useEffect(() => {
    async function loadData() {
      const specs = await listSpecifications();
      setSpecifications(specs);
      const spec = selectedSpecification || specs[0];
      setCurrentSpec(spec);

      if (spec) {
        const reqs = await listRequirements(spec.id);
        setRequirements(reqs);
        const apps = await getApplicabilityAssessments(spec.id);
        setAssessments(apps);
        const gapList = await getSpecificationGaps(spec.id);
        setGaps(gapList);
      }
    }
    loadData();
  }, [selectedSpecification]);

  const stages: PipelineStage[] = [
    { id: 1, name: 'Requirements', subtitle: `${requirements.length} Extracted`, status: 'COMPLETED' },
    { id: 2, name: 'Standards', subtitle: '3 Candidates', status: 'COMPLETED' },
    { id: 3, name: 'Applicability', subtitle: 'IS 12615 APPLICABLE', status: activeStage === 3 ? 'ACTIVE' : 'COMPLETED' },
    { id: 4, name: 'Dependencies', subtitle: 'IS 15999 Test Ref', status: activeStage === 4 ? 'ACTIVE' : 'PENDING' },
    { id: 5, name: 'Currentness', subtitle: '2018 Current / 2011 Superseded', status: activeStage === 5 ? 'ACTIVE' : 'PENDING' },
    { id: 6, name: 'Gaps', subtitle: `${gaps.length || 2} Actionable Gaps`, status: activeStage === 6 ? 'ACTIVE' : 'PENDING' },
    { id: 7, name: 'Decision Package', subtitle: 'Ready for Review', status: 'PENDING' },
  ];

  const handleSpecificationChange = async (specId: number) => {
    const spec = specifications.find((s) => s.id === specId);
    if (spec) {
      setCurrentSpec(spec);
      const reqs = await listRequirements(spec.id);
      setRequirements(reqs);
      const apps = await getApplicabilityAssessments(spec.id);
      setAssessments(apps);
      const gapList = await getSpecificationGaps(spec.id);
      setGaps(gapList);
    }
  };

  const handleCopyGapClause = async (gap: SpecificationGap) => {
    await copyToClipboard(gap.recommended_remedy);
    setCopiedGapId(gap.id);
    setToastMessage(`Copied rectified clause for ${gap.standard_reference || 'Gap'}`);
    setTimeout(() => setCopiedGapId(null), 2000);
  };

  const handleStageSelect = (stageId: number) => {
    if (stageId === 7) {
      onNavigateToDecisionPackage();
    } else {
      setActiveStage(stageId);
    }
  };

  const handleSimulateUpload = () => {
    setIsUploading(true);
    setTimeout(() => {
      setIsUploading(false);
      setToastMessage('Tender specification ingested and parsed successfully.');
    }, 1500);
  };

  return (
    <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Workspace Header & Action Controls */}
      <div className="parchment-card rounded-xl p-5 mb-6">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-[11px] font-mono text-ink-muted mb-1">
              <span>Workspace</span>
              <span>/</span>
              <span>Analyze Specification</span>
              <span>/</span>
              <span className="font-bold text-ink-text">{currentSpec?.tender_reference}</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold font-serif text-ink-text">
              {currentSpec?.title || 'Specification Analysis Workspace'}
            </h1>
            <div className="flex items-center gap-3 text-xs text-ink-muted font-mono mt-1.5 flex-wrap">
              <span>RUN ID: <strong className="text-ink-text">RUN-2025-0418-NV</strong></span>
              <span className="text-slate-300">•</span>
              <span>Source: <strong className="text-ink-text">{currentSpec?.file_name}</strong></span>
              <span className="text-slate-300">•</span>
              {currentSpec && <StatusBadge status={currentSpec.status} size="sm" />}
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            {/* Tender Selector */}
            <select
              value={currentSpec?.id || 1}
              onChange={(e) => handleSpecificationChange(Number(e.target.value))}
              className="px-3 py-2 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text font-mono focus:outline-none focus:border-mineral-blue cursor-pointer"
            >
              {specifications.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.tender_reference} ({s.issuing_organization})
                </option>
              ))}
            </select>

            {/* Quick Demo Sample Tender Button */}
            <button
              onClick={() => {
                handleSpecificationChange(1);
                setToastMessage('Loaded NTPC Thermal Power Station Sample Tender (TND-2024-NTPC-ST-088) with 8 requirements & 2 flagged gaps.');
              }}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded bg-[#2C6E80] hover:bg-[#235866] text-white text-xs font-mono font-medium shadow-xs transition-all cursor-pointer"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-300 animate-pulse" />
              <span>Try Sample Tender (NTPC Rebar)</span>
            </button>

            {/* Ingest / Upload Button */}
            <button
              onClick={handleSimulateUpload}
              disabled={isUploading}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded border border-parchment-border bg-parchment-surface hover:bg-parchment-subtle text-xs font-mono text-ink-text transition-colors shadow-xs cursor-pointer"
            >
              <Upload size={13} className={isUploading ? 'animate-bounce text-mineral-blue' : ''} />
              <span>{isUploading ? 'Ingesting...' : 'Upload Tender PDF'}</span>
            </button>

            {/* View Decision Package Button */}
            <button
              onClick={onNavigateToDecisionPackage}
              className="inline-flex items-center gap-2 px-4 py-2 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <span>View Decision Package</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>

        {/* Demo Notification Banner */}
        <div className="mt-4 pt-3.5 border-t border-parchment-border/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-[#525650] font-serif">
            <span className="font-mono text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-amber-100/80 text-amber-800 border border-amber-300/50">
              AUDIT TRIAL READY
            </span>
            <span>
              Citing superseded <strong>IS 325</strong> for motors instead of mandatory <strong>IS 12615:2018</strong>. Pre-tender corrigendum prepared in Stage 6.
            </span>
          </div>
          <button
            onClick={() => setActiveStage(6)}
            className="text-xs font-mono text-[#2C6E80] hover:underline font-semibold shrink-0 cursor-pointer"
          >
            Jump to Gap & Corrigendum →
          </button>
        </div>
      </div>

      {/* 7-Stage Pipeline Stepper */}
      <PipelineStepper
        stages={stages}
        activeStage={activeStage}
        onSelectStage={handleStageSelect}
      />

      {/* Conditional Rendering: Stage 6 Gaps View vs Default Two-Column Workspace */}
      {activeStage === 6 ? (
        <div className="space-y-6">
          {/* Stage 6 Header Card */}
          <div className="parchment-card rounded-xl p-5 border-l-4 border-l-status-crimson">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <AlertOctagon size={18} className="text-status-crimson" />
                  <h2 className="text-base sm:text-lg font-bold font-serif text-ink-text">
                    Stage 6: Actionable Specification Gaps & Pre-Tender Corrigenda
                  </h2>
                </div>
                <p className="text-xs text-ink-muted">
                  Deterministic audit detected {gaps.length} specification discrepancies requiring pre-tender amendment before publication.
                </p>
              </div>
              <button
                onClick={onNavigateToDecisionPackage}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-colors shrink-0 cursor-pointer"
              >
                <span>Proceed to Decision Package</span>
                <ArrowRight size={13} />
              </button>
            </div>
          </div>

          {/* Gaps List with 1-Click Copy Rectified Clause */}
          <div className="space-y-4">
            {gaps.map((gap) => (
              <div
                key={gap.id}
                className="parchment-card rounded-xl p-5 border border-parchment-border shadow-xs hover:border-[#D9D0C1] transition-all"
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-parchment-border/60 mb-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <StatusBadge status={gap.severity} size="sm" />
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-parchment-subtle text-ink-muted border border-parchment-border">
                      {gap.gap_type}
                    </span>
                    <h3 className="text-sm font-bold font-serif text-ink-text">
                      {gap.title}
                    </h3>
                  </div>

                  {/* 1-Click Copy Rectified Clause Button */}
                  <button
                    onClick={() => handleCopyGapClause(gap)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-mono shrink-0 transition-colors shadow-xs cursor-pointer"
                  >
                    {copiedGapId === gap.id ? (
                      <Check size={12} className="text-emerald-400" />
                    ) : (
                      <Copy size={12} />
                    )}
                    <span>
                      {copiedGapId === gap.id ? 'Clause Copied!' : 'Copy Rectified Clause'}
                    </span>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 text-xs font-mono">
                  <div className="p-3 rounded-lg bg-status-crimsonBg/30 border border-status-crimsonBorder/70">
                    <span className="block text-[10px] text-status-crimson font-bold uppercase mb-1">
                      TENDER CITATION & CONFLICT ({gap.tender_section})
                    </span>
                    <p className="text-ink-text font-serif italic text-xs leading-relaxed">
                      "{gap.tender_excerpt}"
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-status-sageBg/30 border border-status-sageBorder/70">
                    <span className="block text-[10px] text-status-sage font-bold uppercase mb-1">
                      MANDATED BIS STANDARD ({gap.standard_reference})
                    </span>
                    <p className="text-ink-text font-sans text-xs leading-relaxed">
                      {gap.impact_analysis}
                    </p>
                  </div>
                </div>

                {/* Recommended Rectified Clause Excerpt */}
                <div className="p-3 rounded-lg bg-parchment-subtle border border-parchment-border flex items-start gap-2.5">
                  <FileCode size={16} className="text-mineral-blue shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between text-[10px] font-mono uppercase text-ink-muted font-bold mb-1">
                      <span>RECOMMENDED PRE-TENDER CORRIGENDUM CLAUSE</span>
                      <span className="text-status-sage font-semibold">LEGAL AUDIT READY</span>
                    </div>
                    <p className="text-xs font-serif text-ink-text italic leading-relaxed">
                      "{gap.recommended_remedy}"
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Side-by-side Diff Inspector for Visual Reconciliation */}
          <ClauseDiffInspector
            onCopyCorrigendum={() => setToastMessage('Copied recommended addendum clause.')}
          />
        </div>
      ) : (
        /* Main Two-Column Analysis Workspace */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Requirements Extraction */}
          <div className="lg:col-span-6">
            <div className="flex items-center justify-between pb-3 border-b border-parchment-border mb-4">
              <div>
                <h2 className="text-sm font-bold font-serif text-ink-text">
                  Requirements Extraction & Verbatim Evidence
                </h2>
                <p className="text-xs text-ink-muted">
                  Extracted technical parameters with cryptographic offsets from tender PDF.
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-parchment-subtle text-ink-muted border border-parchment-border">
                {requirements.length} Requirements
              </span>
            </div>

            <div className="space-y-4">
              {requirements.map((req) => (
                <RequirementCard
                  key={req.id}
                  requirement={req}
                  onInspectEvidence={(r) => setInspectingReq(r)}
                  onCopyText={() => setToastMessage('Copied verbatim tender excerpt.')}
                />
              ))}
            </div>
          </div>

          {/* Right Column: Standards Applicability & Diff Inspector */}
          <div className="lg:col-span-6">
            <div className="flex items-center justify-between pb-3 border-b border-parchment-border mb-4">
              <div>
                <h2 className="text-sm font-bold font-serif text-ink-text">
                  Standards Applicability & Evidence Matrix
                </h2>
                <p className="text-xs text-ink-muted">
                  Deterministic 8-point evaluation against Bureau of Indian Standards catalog.
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-status-sageBg text-status-sage border border-status-sageBorder font-semibold">
                IS 12615 APPLICABLE
              </span>
            </div>

            {/* Applicability Matrix */}
            {assessments.map((assessment) => (
              <ApplicabilityMatrix
                key={assessment.id}
                assessment={assessment}
                onReevaluate={() => setToastMessage('Re-evaluated applicability with authoritative BIS engine.')}
              />
            ))}

            {/* Clause Diff Inspector */}
            <ClauseDiffInspector
              onCopyCorrigendum={() => setToastMessage('Copied recommended addendum clause.')}
            />
          </div>
        </div>
      )}

      {/* Evidence Provenance Drawer */}
      <EvidenceDrawer
        requirement={inspectingReq}
        isOpen={!!inspectingReq}
        onClose={() => setInspectingReq(null)}
        onCopyHash={() => setToastMessage('Copied SHA-256 offset hash.')}
      />

      {/* Toast Notification */}
      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage(null)} />
      )}
    </div>
  );
};

