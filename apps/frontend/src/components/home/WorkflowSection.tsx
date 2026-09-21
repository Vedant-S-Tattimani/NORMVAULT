import React, { useState } from 'react';
import { 
  FileText, 
  Search, 
  CheckCircle2, 
  GitBranch, 
  Clock, 
  AlertCircle, 
  FileCheck,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface WorkflowSectionProps {
  onNavigate: (view: ViewType) => void;
}

export const WorkflowSection: React.FC<WorkflowSectionProps> = ({ onNavigate }) => {
  const [activeStage, setActiveStage] = useState<number>(0);

  const stages = [
    {
      step: '01',
      title: 'Document Intelligence',
      subtitle: 'Requirement Extraction',
      icon: FileText,
      tag: 'OCR & NLP Engine',
      description:
        'Ingests raw tender PDFs, scans, and technical tender text. Decomposes unstructured procurement documents into atomic requirements with verbatim source citations and page-level provenance.',
      keyOutputs: [
        'Atomic requirement decomposition with unique IDs',
        'Verbatim citation strings with section and page numbers',
        'Extracted parameters: material grades, ratings, test conditions',
      ],
      sampleOutput: 'REQ-01: "All structural steel shall be Fe 410 grade conforming to IS 2062..." [Page 14, Cl 3.2.1]',
    },
    {
      step: '02',
      title: 'Hybrid Retrieval',
      subtitle: 'Standards Catalog Search',
      icon: Search,
      tag: 'BM25 + Dense Vector',
      description:
        'Combines deterministic BM25 lexical keyword matching with dense neural vector embeddings across the authoritative catalog of 22,000+ Bureau of Indian Standards (BIS) publications.',
      keyOutputs: [
        'Candidate standard retrieval with hybrid score fusion (RRF)',
        'Domain-specific expansion (e.g. "TMT bar" -> IS 1786)',
        'Zero-hallucination candidate filtering against active catalog',
      ],
      sampleOutput: 'Retrieved: IS 2062:2011 (Hot Rolled Medium and High Tensile Structural Steel) [Score: 0.942]',
    },
    {
      step: '03',
      title: 'Applicability Engine',
      subtitle: 'Deterministic Verification',
      icon: CheckCircle2,
      tag: '8 Evidence Categories',
      description:
        'Evaluates candidates against 8 rigorous evidence categories: scope, product form, operating parameters, test procedures, safety rules, dimensional limits, environmental conditions, and material grades.',
      keyOutputs: [
        'Category-by-category verification matrix',
        'Deterministic confidence scoring (Highly Relevant / Relevant / Inapplicable)',
        'Verbatim justification for inclusion or exclusion',
      ],
      sampleOutput: 'Verdict: Highly Relevant (8/8 categories verified, 96% confidence score)',
    },
    {
      step: '04',
      title: 'Dependency Graph',
      subtitle: 'Normative Reference Mapping',
      icon: GitBranch,
      tag: 'Graph Intelligence',
      description:
        'Recursively traverses the normative reference graph of the primary standard. Unpacks mandatory companion codes, testing methods, dimensional tolerances, and sampling standards.',
      keyOutputs: [
        'Full dependency tree (Primary Standard -> Mandatory Normative References)',
        'Identifies downstream testing codes (e.g., IS 1608 for Tensile Test)',
        'Prevents incomplete specification traps in tender documents',
      ],
      sampleOutput: 'IS 2062:2011 -> Requires IS 1608:2018 (Tensile Testing) & IS 1599 (Bend Test)',
    },
    {
      step: '05',
      title: 'Currentness & QCO',
      subtitle: 'Edition & Statutory Mandates',
      icon: Clock,
      tag: 'Statutory Verification',
      description:
        'Validates standard currency, tracks historical editions and active amendments, and verifies statutory Quality Control Orders (QCO) issued by DPIIT under Section 16 of the BIS Act 2016.',
      keyOutputs: [
        'Superseded standard detection with active replacement code',
        'Active amendment tracking with technical changes highlighted',
        'Statutory QCO certification mandate validation',
      ],
      sampleOutput: 'Mandatory QCO Detected: DPIIT Steel Products QCO mandates ISI Mark certification',
    },
    {
      step: '06',
      title: 'Specification Gap',
      subtitle: 'Ambiguity & Gap Detection',
      icon: AlertCircle,
      tag: 'Risk Prevention',
      description:
        'Analyzes the tender specification against BIS standard requirements to detect missing parameters, ambiguous tolerances (e.g. "as per engineer"), or conflicting test requirements.',
      keyOutputs: [
        'Severity-classified gap flags (Critical, Warning, Advisory)',
        'Specific missing parameters (e.g. Impact test temperature unspecified)',
        'Actionable clause rectification wording ready to paste into tender',
      ],
      sampleOutput: 'Gap Detected: Sub-grade (E250A/BR/BO) omitted. Recommendation: Specify "E250 Quality BR"',
    },
    {
      step: '07',
      title: 'Decision Package',
      subtitle: 'Cryptographic Audit Seal',
      icon: FileCheck,
      tag: 'SHA-256 Audit Trail',
      description:
        'Synthesizes all intelligence into an exportable, audit-ready Procurement Decision Package with an end-to-end traceability matrix, verifiable SHA-256 cryptographic seal, and CVC compliance certificate.',
      keyOutputs: [
        'Full Clause Traceability Matrix (Tender Clause <-> BIS Clause)',
        'Cryptographic SHA-256 hash seal for tamper detection',
        'Exportable PDF and machine-readable JSON decision package',
      ],
      sampleOutput: 'Package Seal: a3f89e21...b84c [Verified against BIS Catalog Edition v2026.09]',
    },
  ];

  return (
    <section id="workflow-section" className="py-24 px-6 lg:px-12 bg-[#F6F2EA] border-b border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-2">
            THE DETERMINISTIC PIPELINE
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-[2.75rem] font-serif font-bold text-[#1E2320] leading-tight mb-4">
            How NORMVAULT Validates Procurement Specifications
          </h2>
          <p className="text-sm sm:text-base text-[#525650] font-serif leading-relaxed">
            A seven-stage deterministic intelligence architecture that leaves nothing to guesswork—transforming 
            complex engineering tenders into audit-ready, legally compliant procurement decision packages.
          </p>
        </div>

        {/* 7-Step Navigation Chips */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 mb-10">
          {stages.map((stage, idx) => {
            const Icon = stage.icon;
            const isActive = activeStage === idx;
            return (
              <button
                key={stage.step}
                onClick={() => setActiveStage(idx)}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                  isActive
                    ? 'bg-[#1E231D] text-[#FCFAF6] border-[#1E231D] shadow-md -translate-y-0.5'
                    : 'bg-[#FCFAF6] text-[#1E2320] border-[#8C8275]/25 hover:border-[#2C6E80]/50 hover:bg-[#F3EFE7]'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span
                    className={`font-mono text-[10px] font-bold px-1.5 py-0.5 rounded ${
                      isActive ? 'bg-white/20 text-white' : 'bg-[#EAE4D8] text-[#525650]'
                    }`}
                  >
                    {stage.step}
                  </span>
                  <Icon size={14} className={isActive ? 'text-[#64B5F6]' : 'text-[#787165]'} />
                </div>
                <div className="font-serif font-bold text-xs truncate">{stage.title}</div>
                <div
                  className={`text-[10px] truncate mt-0.5 ${
                    isActive ? 'text-white/70' : 'text-[#787165]'
                  }`}
                >
                  {stage.subtitle}
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Stage Deep-Dive Card */}
        <div className="bg-[#FCFAF6] rounded-2xl border border-[#8C8275]/30 p-8 lg:p-10 shadow-sm relative overflow-hidden">
          {/* Subtle Stage Background Accent */}
          <div className="absolute top-0 right-0 p-8 text-[120px] font-mono font-black text-[#1E2320]/3 select-none pointer-events-none leading-none">
            {stages[activeStage].step}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start relative z-10">
            {/* Left Column: Stage Info */}
            <div className="lg:col-span-7">
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#EAE4D8] text-[#2C6E80] text-[10px] font-mono font-semibold uppercase tracking-wider mb-4 border border-[#8C8275]/20">
                <Sparkles size={12} />
                <span>{stages[activeStage].tag}</span>
              </div>

              <h3 className="text-2xl sm:text-3xl font-serif font-bold text-[#1E2320] mb-2">
                Stage {stages[activeStage].step}: {stages[activeStage].title}
              </h3>
              <div className="text-sm font-serif italic text-[#6E726C] mb-5">
                {stages[activeStage].subtitle}
              </div>

              <p className="text-sm text-[#4E524C] leading-relaxed mb-6 font-serif">
                {stages[activeStage].description}
              </p>

              <div>
                <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-[#1E2320] mb-3">
                  Deterministic Deliverables
                </h4>
                <div className="space-y-2.5">
                  {stages[activeStage].keyOutputs.map((out, i) => (
                    <div key={i} className="flex items-start gap-3 text-xs text-[#525650]">
                      <CheckCircle2 size={15} className="text-[#2C6E80] shrink-0 mt-0.5" />
                      <span>{out}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Code/Output Sample Card */}
            <div className="lg:col-span-5 bg-[#1E231D] text-[#ECE7DD] rounded-xl p-6 border border-[#3E4540] font-mono text-xs shadow-inner">
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-white/10 text-[11px] text-[#A6AEA4]">
                <span>STAGE_{stages[activeStage].step}_TELEMETRY</span>
                <span className="text-[#64B5F6] flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#64B5F6] animate-pulse" />
                  VERIFIED
                </span>
              </div>

              <div className="space-y-3">
                <div className="text-[11px] text-[#7E887E]">
                  # Sample output from deterministic pipeline:
                </div>
                <div className="p-3.5 bg-black/40 rounded-lg border border-white/5 text-[#E0DDD5] text-xs leading-relaxed break-words">
                  {stages[activeStage].sampleOutput}
                </div>

                <div className="pt-2 text-[10px] text-[#7E887E] space-y-1">
                  <div>• Latency: &lt; 240ms</div>
                  <div>• Rule Engine: Deterministic Graph v2.4</div>
                  <div>• Audit Trail: SHA-256 Checksummed</div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between">
                <button
                  onClick={() => onNavigate('analyze')}
                  className="text-xs text-[#64B5F6] hover:text-white flex items-center gap-1.5 font-medium transition-colors cursor-pointer"
                >
                  <span>Test on your specification</span>
                  <ArrowRight size={12} />
                </button>
                <span className="text-[10px] text-[#7E887E]">Phase 0–8 Verified</span>
              </div>
            </div>
          </div>
        </div>

        {/* Deep Dive Architecture Link */}
        <div className="mt-10 text-center">
          <button
            onClick={() => onNavigate('how-it-works')}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#1E231D] hover:bg-[#0D100C] text-[#FCFAF6] font-serif font-medium text-xs sm:text-sm shadow-xs transition-all cursor-pointer group"
          >
            <span>Explore Complete 7-Stage Technical Architecture & Methodology</span>
            <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </section>
  );
};
