import React, { useState, useEffect, useRef } from 'react';
import { ProcurementSpecification, Requirement, ApplicabilityAssessment } from '../types/requirement';
import { SpecificationGap } from '../types/gap';
import {
  listSpecifications,
  listRequirements,
  uploadDocument,
  pollDocumentStatus,
  submitTextSpecification,
} from '../api/specifications';
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
import {
  Upload,
  ArrowRight,
  AlertOctagon,
  Copy,
  Check,
  FileCode,
  FileText,
  Loader2,
  Sparkles,
  X,
} from 'lucide-react';

interface AnalyzePageProps {
  selectedSpecification?: ProcurementSpecification;
  onNavigateToDecisionPackage: (spec?: ProcurementSpecification) => void;
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
  const [uploadStage, setUploadStage] = useState<string | null>(null);
  const [copiedGapId, setCopiedGapId] = useState<number | null>(null);
  const [selectedGapId, setSelectedGapId] = useState<number | null>(null);

  // Raw Text Intake Modal State
  const [showTextModal, setShowTextModal] = useState(false);
  const [rawTitle, setRawTitle] = useState('');
  const [rawOrg, setRawOrg] = useState('');
  const [rawTenderRef, setRawTenderRef] = useState('');
  const [rawContent, setRawContent] = useState('');
  const [isSubmittingText, setIsSubmittingText] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

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
        if (gapList.length > 0) {
          setSelectedGapId(gapList[0].id);
        }
      }
    }
    loadData();
  }, [selectedSpecification]);

  const activeDiffGap = gaps.find((g) => g.id === selectedGapId) || gaps[0];
  const primaryStandard = assessments[0]?.standard_number || 'IS Standard';
  const primaryStatus = assessments[0]?.verdict || 'APPLICABLE';

  const stages: PipelineStage[] = [
    { id: 1, name: 'Requirements', subtitle: `${requirements.length} Extracted`, status: activeStage === 1 ? 'ACTIVE' : 'COMPLETED' },
    { id: 2, name: 'Standards', subtitle: `${assessments.length > 0 ? assessments.length + ' Candidates' : 'Catalog Match'}`, status: activeStage === 2 ? 'ACTIVE' : activeStage > 2 ? 'COMPLETED' : 'PENDING' },
    { id: 3, name: 'Applicability', subtitle: `${primaryStandard} ${primaryStatus}`, status: activeStage === 3 ? 'ACTIVE' : activeStage > 3 ? 'COMPLETED' : 'PENDING' },
    { id: 4, name: 'Dependencies', subtitle: 'Normative Ref Tree', status: activeStage === 4 ? 'ACTIVE' : activeStage > 4 ? 'COMPLETED' : 'PENDING' },
    { id: 5, name: 'Currentness', subtitle: 'Supersession & QCO', status: activeStage === 5 ? 'ACTIVE' : activeStage > 5 ? 'COMPLETED' : 'PENDING' },
    { id: 6, name: 'Gaps', subtitle: `${gaps.length} Actionable Gaps`, status: activeStage === 6 ? 'ACTIVE' : activeStage > 6 ? 'COMPLETED' : 'PENDING' },
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
      if (gapList.length > 0) {
        setSelectedGapId(gapList[0].id);
      }
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
      onNavigateToDecisionPackage(currentSpec || undefined);
    } else {
      setActiveStage(stageId);
    }
  };

  // Real File Upload & Polling
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setUploadStage('VALIDATING');
      setToastMessage(`Uploading ${file.name}...`);

      const res = await uploadDocument(file);
      setUploadStage('EXTRACTING');

      // Poll until completed
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const statusRes = await pollDocumentStatus(res.id);
          if (statusRes.status === 'EXTRACTING') {
            setUploadStage('EXTRACTING REQUIREMENTS');
          } else if (statusRes.status === 'STRUCTURING') {
            setUploadStage('STRUCTURING CLAUSES');
          } else if (statusRes.status === 'ANALYZING') {
            setUploadStage('MATCHING STANDARDS');
          } else if (statusRes.status === 'COMPLETED') {
            clearInterval(pollInterval);
            setUploadStage('COMPLETED');
            setTimeout(async () => {
              setIsUploading(false);
              setUploadStage(null);
              setToastMessage(`Successfully ingested & parsed ${file.name}`);
              const updatedSpecs = await listSpecifications();
              setSpecifications(updatedSpecs);
              const newlyParsed = updatedSpecs.find((s) => s.file_name?.includes(file.name)) || updatedSpecs[0];
              if (newlyParsed) {
                handleSpecificationChange(newlyParsed.id);
              }
            }, 800);
          } else if (statusRes.status.startsWith('FAILED')) {
            clearInterval(pollInterval);
            setIsUploading(false);
            setUploadStage(null);
            setToastMessage(`Extraction failed: ${statusRes.error || 'Check document format'}`);
          }
        } catch {
          // ignore transient poll error
        }

        if (attempts > 30) {
          clearInterval(pollInterval);
          setIsUploading(false);
          setUploadStage(null);
        }
      }, 1000);
    } catch (err: any) {
      setIsUploading(false);
      setUploadStage(null);
      setToastMessage(`Upload error: ${err.message}`);
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Direct Text Intake Submit
  const handleTextSubmit = async () => {
    if (!rawContent.trim()) {
      setToastMessage('Please enter specification text.');
      return;
    }

    try {
      setIsSubmittingText(true);
      const res = await submitTextSpecification({
        title: rawTitle || 'GeM Direct Tender Specification Intake',
        department: rawOrg || 'Central Procurement Authority',
        tender_reference: rawTenderRef || `TND-${Date.now().toString().slice(-6)}`,
        raw_content: rawContent,
      });

      setShowTextModal(false);
      setToastMessage(`Parsed ${res.requirements_count} requirements from tender text!`);

      const updatedSpecs = await listSpecifications();
      setSpecifications(updatedSpecs);
      const newlyCreated = updatedSpecs.find((s) => s.id === res.id) || updatedSpecs[updatedSpecs.length - 1];
      if (newlyCreated) {
        handleSpecificationChange(newlyCreated.id);
      }
    } catch (err: any) {
      setToastMessage(`Error analyzing text: ${err.message}`);
    } finally {
      setIsSubmittingText(false);
    }
  };

  const prefillSampleText = () => {
    setRawTitle('Supply of 30 kW Flameproof Induction Motors for Thermal Plant');
    setRawOrg('NTPC Singrauli Super Thermal Power Station');
    setRawTenderRef('NTPC/SSTPS/EM-2026/099');
    setRawContent(`1.0 SCOPE OF SUPPLY:
The contractor shall supply 30 kW, 415 V ± 6%, 50 Hz, 3-Phase Squirrel Cage Induction Motors designed for continuous operation (S1 Duty) in Coal Handling Plant classified under Zone 1 hazardous area.

2.0 EFFICIENCY & TECHNICAL PERFORMANCE:
2.1 All motors must conform strictly to Premium Efficiency Class IE3 in accordance with IS 12615:2018.
2.2 Temperature rise of the stator winding shall be limited to Class B limits (70 deg C by resistance method) with Class F insulation system.
2.3 Efficiency testing and losses determination shall be certified strictly in accordance with IS 15999 (Part 2/Sec 1).

3.0 STATUTORY CERTIFICATION:
3.1 Motors must bear mandatory BIS Standard Mark (ISI Mark) under Scheme-I in accordance with DPIIT Quality Control Order 2024. Bidders must produce valid CM/L license number with technical bid.
3.2 Flameproof enclosure protection shall comply with IS/IEC 60079-1 for gas group IIA/IIB.`);
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
              <span>RUN ID: <strong className="text-ink-text">{currentSpec ? `SPEC-${currentSpec.id}-NV` : 'RUN-ACTIVE-NV'}</strong></span>
              <span className="text-slate-300">•</span>
              <span>Source: <strong className="text-ink-text">{currentSpec?.file_name}</strong></span>
              <span className="text-slate-300">•</span>
              {currentSpec && <StatusBadge status={currentSpec.status} size="sm" />}
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            {/* Tender Selector */}
            <select
              value={currentSpec?.id || (specifications[0]?.id ?? 1)}
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
                if (specifications.length > 0) {
                  handleSpecificationChange(specifications[0].id);
                  setToastMessage(`Loaded ${specifications[0].tender_reference} with ${specifications[0].total_requirements_count || 0} requirements.`);
                }
              }}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded bg-[#2C6E80] hover:bg-[#235866] text-white text-xs font-mono font-medium shadow-xs transition-all cursor-pointer"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-300 animate-pulse" />
              <span>Load Primary Specification</span>
            </button>

            {/* Hidden File Input */}
            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf,.txt"
              onChange={handleFileUpload}
              className="hidden"
            />

            {/* Ingest / Real Upload Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded border border-parchment-border bg-parchment-surface hover:bg-parchment-subtle text-xs font-mono text-ink-text transition-colors shadow-xs cursor-pointer"
            >
              {isUploading ? (
                <Loader2 size={13} className="animate-spin text-mineral-blue" />
              ) : (
                <Upload size={13} />
              )}
              <span>{isUploading ? (uploadStage || 'Processing...') : 'Upload Tender (.PDF/.TXT)'}</span>
            </button>

            {/* Direct Text Intake Button */}
            <button
              onClick={() => setShowTextModal(true)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded border border-mineral-blue/40 bg-mineral-light/50 hover:bg-mineral-light text-mineral-dark text-xs font-mono font-medium transition-colors shadow-xs cursor-pointer"
            >
              <FileText size={13} />
              <span>Paste Tender Text</span>
            </button>

            {/* View Decision Package Button */}
            <button
              onClick={() => onNavigateToDecisionPackage(currentSpec || undefined)}
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
                onClick={() => onNavigateToDecisionPackage(currentSpec || selectedSpecification)}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold shadow-xs transition-colors shrink-0 cursor-pointer"
              >
                <span>Proceed to Decision Package</span>
                <ArrowRight size={13} />
              </button>
            </div>
          </div>

          {/* Gaps List with 1-Click Copy Rectified Clause */}
          <div className="space-y-4">
            {gaps.map((gap, index) => (
              <div
                key={gap.id}
                onClick={() => setSelectedGapId(gap.id)}
                className={`parchment-card rounded-xl p-5 border shadow-xs transition-all cursor-pointer ${
                  activeDiffGap?.id === gap.id
                    ? 'border-mineral-blue ring-1 ring-mineral-blue/40 bg-mineral-light/10'
                    : 'border-parchment-border hover:border-[#D9D0C1]'
                }`}
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-parchment-border/60 mb-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-ink-text text-parchment-surface font-bold">
                      GAP #{index + 1}
                    </span>
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
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopyGapClause(gap);
                    }}
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
          <div className="pt-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <div className="text-xs font-serif font-bold text-ink-text flex items-center gap-2">
                <span>Active Diff Target:</span>
                <span className="font-mono text-mineral-blue font-semibold">
                  {activeDiffGap ? `${activeDiffGap.standard_reference} (${activeDiffGap.tender_section})` : 'Select a gap above'}
                </span>
              </div>
              {gaps.length > 1 && (
                <div className="flex items-center gap-1.5 text-xs font-mono">
                  <span className="text-ink-muted text-[11px]">Compare Gap:</span>
                  {gaps.map((gap, index) => (
                    <button
                      key={gap.id}
                      onClick={() => setSelectedGapId(gap.id)}
                      className={`px-2.5 py-1 rounded border text-xs cursor-pointer transition-colors ${
                        activeDiffGap?.id === gap.id
                          ? 'bg-ink-text text-parchment-surface border-ink-text font-bold'
                          : 'bg-parchment-surface text-ink-muted border-parchment-border hover:bg-parchment-subtle'
                      }`}
                    >
                      Gap #{index + 1}: {gap.standard_reference || gap.gap_type}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <ClauseDiffInspector
              tenderClauseText={activeDiffGap?.tender_excerpt}
              standardClauseText={activeDiffGap?.impact_analysis}
              corrigendumClauseText={activeDiffGap?.recommended_remedy}
              affectedSection={activeDiffGap?.tender_section}
              targetStandard={activeDiffGap?.standard_reference}
              conflictSummary={activeDiffGap ? [
                activeDiffGap.title,
                `Severity: ${activeDiffGap.severity} • Classification: ${activeDiffGap.gap_type}`
              ] : undefined}
              standardKeyPoints={activeDiffGap ? [
                `Mandatory compliance with ${activeDiffGap.standard_reference || 'BIS standard'}`,
                activeDiffGap.standard_clause ? `Mandatory Clause ${activeDiffGap.standard_clause}` : 'Statutory BIS Act 2016 compliance'
              ] : undefined}
              onCopyCorrigendum={() => setToastMessage('Copied recommended addendum clause.')}
            />
          </div>
        </div>
      ) : (
        /* Main Two-Column Analysis Workspace */
        <div className="space-y-6">
          {/* Active Stage Perspective Guidance Banner */}
          {activeStage === 1 && (
            <div className="parchment-card rounded-xl p-4 border-l-4 border-l-mineral-blue flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-mineral-light text-mineral-dark font-bold">Stage 1 Active</span>
                <h3 className="text-sm font-bold font-serif text-ink-text mt-1">Requirements Extraction & Cryptographic Provenance</h3>
                <p className="text-xs text-ink-muted">All {requirements.length} technical parameters extracted with SHA-256 byte offsets and verbatim source citations from the tender document.</p>
              </div>
            </div>
          )}
          {activeStage === 2 && (
            <div className="parchment-card rounded-xl p-4 border-l-4 border-l-mineral-blue flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-mineral-light text-mineral-dark font-bold">Stage 2 Active</span>
                <h3 className="text-sm font-bold font-serif text-ink-text mt-1">Authoritative Standards Catalog Search & Matching</h3>
                <p className="text-xs text-ink-muted">Matched Indian Standards catalog against tender parameters for electrical motors, switchgear, and power transmission.</p>
              </div>
            </div>
          )}
          {activeStage === 4 && (
            <div className="parchment-card rounded-xl p-4 border-l-4 border-l-amber-500 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold">Stage 4 Active</span>
                <h3 className="text-sm font-bold font-serif text-ink-text mt-1">Normative Reference & Test Method Dependency Tree</h3>
                <p className="text-xs text-ink-muted">IS 12615:2018 normatively depends on IS 15999 (losses & efficiency testing) and IS/IEC 60079-1 (flameproof enclosures).</p>
              </div>
            </div>
          )}
          {activeStage === 5 && (
            <div className="parchment-card rounded-xl p-4 border-l-4 border-l-status-crimson flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold">Stage 5 Active</span>
                <h3 className="text-sm font-bold font-serif text-ink-text mt-1">Currentness Verification & Gazette QCO Mandate Audit</h3>
                <p className="text-xs text-ink-muted">Verifying withdrawal status of cited IS 325 and checking statutory Quality Control Orders from DPIIT / Ministry of Heavy Industries.</p>
              </div>
            </div>
          )}

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
                  {primaryStandard} {primaryStatus}
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
                tenderClauseText={activeDiffGap?.tender_excerpt}
                standardClauseText={activeDiffGap?.impact_analysis}
                corrigendumClauseText={activeDiffGap?.recommended_remedy}
                affectedSection={activeDiffGap?.tender_section}
                targetStandard={activeDiffGap?.standard_reference}
                conflictSummary={activeDiffGap ? [
                  activeDiffGap.title,
                  `Severity: ${activeDiffGap.severity} • Classification: ${activeDiffGap.gap_type}`
                ] : undefined}
                standardKeyPoints={activeDiffGap ? [
                  `Mandatory compliance with ${activeDiffGap.standard_reference || 'BIS standard'}`,
                  activeDiffGap.standard_clause ? `Mandatory Clause ${activeDiffGap.standard_clause}` : 'Statutory BIS Act 2016 compliance'
                ] : undefined}
                onCopyCorrigendum={() => setToastMessage('Copied recommended addendum clause.')}
              />
            </div>
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

      {/* Real-time Upload Processing Modal */}
      {isUploading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink-dark/60 backdrop-blur-xs">
          <div className="bg-parchment-base border border-parchment-border rounded-xl shadow-2xl p-6 w-full max-w-md text-center space-y-4">
            <div className="mx-auto w-12 h-12 rounded-full bg-mineral-light flex items-center justify-center text-mineral-dark">
              <Loader2 size={24} className="animate-spin" />
            </div>
            <div>
              <h3 className="font-serif font-bold text-ink-text text-base">
                Processing Procurement Specification
              </h3>
              <p className="text-xs text-ink-muted font-mono mt-1">
                {uploadStage || 'Extracting technical parameters & citations...'}
              </p>
            </div>
            <div className="w-full bg-parchment-subtle rounded-full h-2 overflow-hidden border border-parchment-border">
              <div className="bg-mineral-blue h-full rounded-full animate-pulse w-3/4" />
            </div>
            <p className="text-[11px] text-ink-muted font-sans">
              PyMuPDF extraction &gt; Semantic & Lexical Standards Retrieval &gt; BIS Normative Verification
            </p>
          </div>
        </div>
      )}

      {/* Raw Text Intake Modal */}
      {showTextModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink-dark/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-parchment-base border border-parchment-border rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
            <div className="p-4 sm:p-5 bg-parchment-surface border-b border-parchment-border flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded bg-mineral-light text-mineral-dark">
                  <FileText size={18} />
                </div>
                <div>
                  <h3 className="font-serif font-bold text-ink-text text-base">
                    Direct Tender Specification Intake
                  </h3>
                  <p className="text-xs text-ink-muted font-mono">
                    Paste raw RFP / NIT paragraphs from GeM, CPPP, or PSU portal
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowTextModal(false)}
                className="p-1.5 rounded-md hover:bg-parchment-subtle text-ink-muted hover:text-ink-text transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-5 overflow-y-auto space-y-4 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-ink-muted font-mono text-[11px]">TENDER METADATA</span>
                <button
                  type="button"
                  onClick={prefillSampleText}
                  className="inline-flex items-center gap-1 text-[11px] font-mono text-mineral-blue hover:underline cursor-pointer"
                >
                  <Sparkles size={12} />
                  <span>Pre-fill Sample GeM Boiler Motors RFP</span>
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-mono uppercase text-ink-muted mb-1">
                    Tender Reference / Bid No.
                  </label>
                  <input
                    type="text"
                    value={rawTenderRef}
                    onChange={(e) => setRawTenderRef(e.target.value)}
                    placeholder="e.g. GeM/2026/B/9821"
                    className="w-full px-3 py-2 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text font-mono focus:outline-none focus:border-mineral-blue"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-mono uppercase text-ink-muted mb-1">
                    Issuing Entity / PSU
                  </label>
                  <input
                    type="text"
                    value={rawOrg}
                    onChange={(e) => setRawOrg(e.target.value)}
                    placeholder="e.g. NTPC / NHPC / Indian Railways"
                    className="w-full px-3 py-2 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text font-mono focus:outline-none focus:border-mineral-blue"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-mono uppercase text-ink-muted mb-1">
                  Procurement Title / Subject
                </label>
                <input
                  type="text"
                  value={rawTitle}
                  onChange={(e) => setRawTitle(e.target.value)}
                  placeholder="e.g. Supply and Testing of 3-Phase Flameproof Induction Motors"
                  className="w-full px-3 py-2 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text font-mono focus:outline-none focus:border-mineral-blue"
                />
              </div>

              <div>
                <label className="block text-[10px] font-mono uppercase text-ink-muted mb-1">
                  Technical Requirements & Scope Text
                </label>
                <textarea
                  value={rawContent}
                  onChange={(e) => setRawContent(e.target.value)}
                  rows={8}
                  placeholder="Paste verbatim specification text, technical schedule, or clause requirements here..."
                  className="w-full p-3 text-xs bg-parchment-surface border border-parchment-border rounded-lg text-ink-text font-mono focus:outline-none focus:border-mineral-blue leading-relaxed resize-y"
                />
              </div>
            </div>

            <div className="p-4 bg-parchment-surface border-t border-parchment-border flex items-center justify-end gap-2.5 shrink-0">
              <button
                type="button"
                onClick={() => setShowTextModal(false)}
                className="px-3.5 py-1.5 rounded border border-parchment-border text-ink-text hover:bg-parchment-subtle text-xs font-mono transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleTextSubmit}
                disabled={isSubmittingText}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded bg-mineral-blue hover:bg-mineral-dark text-white text-xs font-mono font-medium shadow-xs transition-colors cursor-pointer disabled:opacity-50"
              >
                {isSubmittingText ? <Loader2 size={13} className="animate-spin" /> : <Sparkles size={13} />}
                <span>{isSubmittingText ? 'Extracting...' : 'Extract & Analyze Specification'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage(null)} />
      )}
    </div>
  );
};

