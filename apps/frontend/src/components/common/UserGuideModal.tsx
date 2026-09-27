import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ViewType } from './EditorialHeader';
import {
  X,
  Compass,
  CheckCircle2,
  ArrowRight,
  BookOpen,
  Layers,
  FileCheck,
  Cpu,
  Search,
  ExternalLink,
  Sparkles,
} from 'lucide-react';

interface UserGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (view: ViewType) => void;
}

interface FeatureItem {
  id: string;
  view: ViewType;
  title: string;
  badge: string;
  screenshot: string;
  summary: string;
  howToUse: string[];
  keyHighlights: string[];
}

export const UserGuideModal: React.FC<UserGuideModalProps> = ({
  isOpen,
  onClose,
  onNavigate,
}) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'quickstart' | 'features' | 'workflow' | 'glossary'>('quickstart');
  const [selectedFeatureId, setSelectedFeatureId] = useState<string>('workspace');
  const [searchFilter, setSearchFilter] = useState('');

  if (!isOpen) return null;

  const features: FeatureItem[] = [
    {
      id: 'workspace',
      view: 'analyze',
      title: 'Workspace & Specification Intake',
      badge: 'Core Engine • Stages 1–6',
      screenshot: '/screenshots/02_workspace_analyze.png',
      summary: 'The heart of NORMVAULT. Ingests tender PDFs or raw clause text, extracts atomic requirements with SHA-256 byte offsets, matches Indian Standards, runs 8-point applicability tests, and flags specification gaps.',
      howToUse: [
        'Select an existing tender from the dropdown or click "Upload Specification" to upload your tender document.',
        'Review the Pipeline Stepper at the top showing the 7 progress stages.',
        'Navigate between "Extracted Requirements", "Applicability Matrix", and "Clause Diff Inspector".',
        'Review detected gaps and click "Copy Corrigendum Addendum" to draft instant pre-tender amendments.'
      ],
      keyHighlights: [
        'Zero AI Hallucination: Standard suggestions strictly validated against verified BIS catalog.',
        'Deterministic 8-Point Matrix: Scope, Operating Parameters, Material Grades, Tolerances, and QCOs.',
        'Verbatim Page & Clause Citations with SHA-256 cryptographic byte-offsets.'
      ]
    },
    {
      id: 'standards',
      view: 'standards',
      title: 'BIS Standards Registry Explorer',
      badge: '22,000+ Codes • Hybrid Search',
      screenshot: '/screenshots/03_standards_registry.png',
      summary: 'Authoritative catalog of Bureau of Indian Standards (BIS). Features reciprocal rank fusion combining lexical BM25 and dense neural vector search for lightning-fast standard discovery.',
      howToUse: [
        'Use the top search input to type either an IS code (e.g., "IS 12615", "IS 1786") or engineering keywords (e.g., "3-phase motor", "TMT bars").',
        'Filter by Category (Electrical, Civil, Mechanical, Metallurgical) or Status (Current, Superseded, Under Review).',
        'Click on any standard card to inspect its Edition history, normative dependencies, and DPIIT Quality Control Orders.'
      ],
      keyHighlights: [
        'Lifecycle & Supersession alerts: Instantly flags withdrawn standards like IS 325.',
        'DPIIT QCO Badges: Highlights statutory products where ISI mark is legally mandatory under Section 16 of the BIS Act.'
      ]
    },
    {
      id: 'decision-package',
      view: 'decision-package',
      title: 'Cryptographic Decision Package',
      badge: 'CVC / CAG Defensible Audit Seal',
      screenshot: '/screenshots/04_decision_package.png',
      summary: 'The final, unassailable audit artifact. Synthesizes all findings, full clause traceability matrix, and corrigenda into an immutable memorandum protected by SHA-256 digital seals.',
      howToUse: [
        'Select your analyzed tender from the header dropdown.',
        'Verify the live SHA-256 package digest and compliance certificate.',
        'Inspect the End-to-End Clause Traceability Matrix linking tender requirements to BIS standard clauses.',
        'Click "Export Decision Package (JSON)" or "Print / Export Executive Memorandum" for CVC/CAG files.'
      ],
      keyHighlights: [
        '100% CVC & CAG Audit Defensibility: Prevents procurement vigilance queries.',
        'Signed Clause-by-Clause Reconciliation Matrix with legal citations.'
      ]
    },
    {
      id: 'dashboard',
      view: 'dashboard',
      title: 'Executive Procurement Dashboard',
      badge: 'Portfolio Health & Risk Metrics',
      screenshot: '/screenshots/05_executive_dashboard.png',
      summary: 'High-level bird’s-eye perspective for Senior Procurement Officers, Chief Vigilance Officers (CVOs), and Tender Committees to monitor compliance risk across all active tenders.',
      howToUse: [
        'Inspect key health KPIs: Active Tenders, Total Analyzed Value, High-Risk Gaps, and Audit Readiness.',
        'Filter tenders by Status: "Action Required", "Ready for Tender", "Audit Ready".',
        'Click any tender row to jump straight into its full Workspace analysis.'
      ],
      keyHighlights: [
        'Real-time risk quantification: Flags tenders with blocking superseded standards.',
        'Instant multi-tender compliance status overview.'
      ]
    },
    {
      id: 'bidder',
      view: 'comparative',
      title: 'Bidder Compliance & Comparative Evaluation',
      badge: 'Multi-Bidder Scoring • Technical TEC',
      screenshot: '/screenshots/06_bidder_evaluation.png',
      summary: 'Evaluates competing vendor bids against mandated Indian Standards during Technical Evaluation Committee (TEC) review to eliminate non-compliant or deviant offers.',
      howToUse: [
        'Select the active procurement package.',
        'View the comparative vendor matrix scoring each bidder against mandatory standard criteria.',
        'Identify deviations, missing test certificates, and non-compliance flags before opening financial bids.'
      ],
      keyHighlights: [
        'Eliminates subjective evaluator bias in technical bid evaluation.',
        'Automated detection of non-conforming technical specifications in vendor bids.'
      ]
    },
    {
      id: 'benchmarks',
      view: 'benchmarks',
      title: 'Algorithmic Benchmarks & Retrieval Quality',
      badge: 'Precision@k • RRF Evaluation',
      screenshot: '/screenshots/07_benchmarks.png',
      summary: 'Transparent, scientific proof of NORMVAULT’s retrieval engine performance compared to pure lexical BM25 and pure dense vector retrieval.',
      howToUse: [
        'Explore Precision@1, Precision@5, Mean Reciprocal Rank (MRR), and Recall metrics across gold-standard tender datasets.',
        'Review the ablation comparisons proving why Reciprocal Rank Fusion (RRF) prevents hallucinations.'
      ],
      keyHighlights: [
        'Empirical verification: 96.4% Precision@1 on public sector Indian tender benchmarks.',
        'Full transparency for technical auditors and data science reviewers.'
      ]
    },
    {
      id: 'methodology',
      view: 'how-it-works',
      title: '7-Stage Deterministic Architecture',
      badge: 'Platform Methodology Deep Dive',
      screenshot: '/screenshots/08_how_it_works.png',
      summary: 'Detailed architectural walkthrough explaining each of the 7 stages: Extraction, Hybrid Retrieval, 8-Point Matrix, Dependency Graph, Currentness/QCO, Gap Detection, and Decision Package.',
      howToUse: [
        'Click any of the 7 stage tabs to inspect algorithmic mechanisms, mathematical inputs/outputs, and real-world NTPC/NHPC tender executions.'
      ],
      keyHighlights: [
        'Interactive stage-by-stage pipeline inspection with sample tender JSON payloads.'
      ]
    }
  ];

  const filteredFeatures = features.filter((f) =>
    f.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
    f.summary.toLowerCase().includes(searchFilter.toLowerCase()) ||
    f.badge.toLowerCase().includes(searchFilter.toLowerCase())
  );

  const selectedFeature = features.find((f) => f.id === selectedFeatureId) || features[0];

  const handleNavigateAndClose = (view: ViewType) => {
    onNavigate(view);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-[#FCFAF6] border border-[#8C8275]/40 rounded-2xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden font-sans text-[#1E2320]">
        {/* Modal Top Header */}
        <div className="px-6 py-4 bg-[#EDE7DB] border-b border-[#8C8275]/25 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[#1E231D] text-parchment-surface flex items-center justify-center">
              <Compass size={20} className="text-[#2C6E80]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-serif font-bold text-[#1E2320]">
                  {t('guide_modal_title', 'NORMVAULT New User & Feature Guide')}
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#E5F0F2] text-[#2C6E80] font-semibold border border-[#2C6E80]/30">
                  Interactive Walkthrough
                </span>
              </div>
              <p className="text-xs text-[#525650] font-serif">
                {t('guide_modal_sub', 'Step-by-step instructions to master evidence-backed Indian Standards procurement intelligence.')}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#787165] hover:text-[#1E2320] hover:bg-[#E2DACB] transition-colors cursor-pointer"
            title="Close Guide (Esc)"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="px-6 bg-[#F6F2EA] border-b border-[#8C8275]/20 flex items-center gap-6 text-xs font-mono">
          <button
            onClick={() => setActiveTab('quickstart')}
            className={`py-3 font-semibold border-b-2 transition-colors cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'quickstart'
                ? 'border-[#2C6E80] text-[#2C6E80]'
                : 'border-transparent text-[#787165] hover:text-[#1E2320]'
            }`}
          >
            <Sparkles size={14} />
            <span>{t('guide_tab_quickstart', '3-Minute Quickstart')}</span>
          </button>
          <button
            onClick={() => setActiveTab('features')}
            className={`py-3 font-semibold border-b-2 transition-colors cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'features'
                ? 'border-[#2C6E80] text-[#2C6E80]'
                : 'border-transparent text-[#787165] hover:text-[#1E2320]'
            }`}
          >
            <Layers size={14} />
            <span>{t('guide_tab_features', 'Step-by-Step Feature Walkthrough')} ({features.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('workflow')}
            className={`py-3 font-semibold border-b-2 transition-colors cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'workflow'
                ? 'border-[#2C6E80] text-[#2C6E80]'
                : 'border-transparent text-[#787165] hover:text-[#1E2320]'
            }`}
          >
            <Cpu size={14} />
            <span>{t('guide_tab_pipeline', 'The 7-Stage Pipeline')}</span>
          </button>
          <button
            onClick={() => setActiveTab('glossary')}
            className={`py-3 font-semibold border-b-2 transition-colors cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'glossary'
                ? 'border-[#2C6E80] text-[#2C6E80]'
                : 'border-transparent text-[#787165] hover:text-[#1E2320]'
            }`}
          >
            <BookOpen size={14} />
            <span>Statutory Rules & Checklist</span>
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-[#FCFAF6]">
          {/* TAB 1: QUICKSTART */}
          {activeTab === 'quickstart' && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-[#EDE7DB] border border-[#8C8275]/25">
                <h3 className="font-serif font-bold text-base text-[#1E2320] mb-1">
                  Welcome to NORMVAULT
                </h3>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  NORMVAULT safeguards public procurement officers against tender litigation, vendor arbitration, and vigilance audits by deterministically mapping technical tender requirements to verified <strong>Bureau of Indian Standards (BIS)</strong> codes, enforcing <strong>DPIIT Quality Control Orders (QCOs)</strong>, and generating ready-to-issue pre-tender corrigenda.
                </p>
              </div>

              {/* 3 Step Flow */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Step 1 */}
                <div className="p-5 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25 flex flex-col justify-between">
                  <div>
                    <div className="w-8 h-8 rounded-full bg-[#1E231D] text-white flex items-center justify-center font-mono font-bold text-xs mb-3">
                      01
                    </div>
                    <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-2">
                      Select or Ingest Tender Specification
                    </h4>
                    <p className="text-xs text-[#525650] font-serif leading-relaxed mb-4">
                      Choose an existing sample tender (like the NTPC 15kW Motor Tender or NHPC 33kV Switchgear) from the dropdown, or click "Upload Specification" to parse your own document.
                    </p>
                  </div>
                  <button
                    onClick={() => handleNavigateAndClose('analyze')}
                    className="inline-flex items-center justify-between w-full px-3 py-2 rounded bg-[#EAE4D8] hover:bg-[#DFD7C7] text-xs font-mono font-semibold text-[#1E2320] transition-colors cursor-pointer"
                  >
                    <span>Open Workspace</span>
                    <ArrowRight size={14} />
                  </button>
                </div>

                {/* Step 2 */}
                <div className="p-5 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25 flex flex-col justify-between">
                  <div>
                    <div className="w-8 h-8 rounded-full bg-[#2C6E80] text-white flex items-center justify-center font-mono font-bold text-xs mb-3">
                      02
                    </div>
                    <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-2">
                      Review Applicability & Resolve Gaps
                    </h4>
                    <p className="text-xs text-[#525650] font-serif leading-relaxed mb-4">
                      Inspect the 8-point applicability matrix. Check the "Clause Diff Inspector" to identify contradictory voltage limits or withdrawn standards, and copy the ready-to-issue corrigendum.
                    </p>
                  </div>
                  <button
                    onClick={() => handleNavigateAndClose('analyze')}
                    className="inline-flex items-center justify-between w-full px-3 py-2 rounded bg-[#EAE4D8] hover:bg-[#DFD7C7] text-xs font-mono font-semibold text-[#1E2320] transition-colors cursor-pointer"
                  >
                    <span>Inspect Clause Diff</span>
                    <ArrowRight size={14} />
                  </button>
                </div>

                {/* Step 3 */}
                <div className="p-5 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25 flex flex-col justify-between">
                  <div>
                    <div className="w-8 h-8 rounded-full bg-[#3D704D] text-white flex items-center justify-center font-mono font-bold text-xs mb-3">
                      03
                    </div>
                    <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-2">
                      Export Audit-Sealed Decision Package
                    </h4>
                    <p className="text-xs text-[#525650] font-serif leading-relaxed mb-4">
                      Lock in your procurement intelligence package with a tamper-evident SHA-256 digital digest and export printable executive memoranda for CVC, CAG, or tender committee files.
                    </p>
                  </div>
                  <button
                    onClick={() => handleNavigateAndClose('decision-package')}
                    className="inline-flex items-center justify-between w-full px-3 py-2 rounded bg-[#EAE4D8] hover:bg-[#DFD7C7] text-xs font-mono font-semibold text-[#1E2320] transition-colors cursor-pointer"
                  >
                    <span>View Decision Package</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>

              {/* Quick Navigation Cards */}
              <div className="p-4 rounded-xl bg-[#E5F0F2]/40 border border-[#2C6E80]/20 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <BookOpen size={20} className="text-[#2C6E80] shrink-0" />
                  <div>
                    <div className="text-xs font-mono font-bold text-[#1E2320]">
                      Looking to look up a specific Indian Standard?
                    </div>
                    <div className="text-xs text-[#525650] font-serif">
                      Access 22,000+ Indian Standards in the registry with instant supersession & QCO notification lookups.
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleNavigateAndClose('standards')}
                  className="px-4 py-2 bg-[#2C6E80] hover:bg-[#235866] text-white text-xs font-mono font-semibold rounded-lg shrink-0 transition-colors cursor-pointer"
                >
                  Explore BIS Standards
                </button>
              </div>
            </div>
          )}

          {/* TAB 2: STEP-BY-STEP FEATURE WALKTHROUGH */}
          {activeTab === 'features' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Feature Selection Sidebar */}
              <div className="lg:col-span-4 space-y-2">
                <div className="relative mb-3">
                  <Search size={14} className="absolute left-3 top-2.5 text-[#787165]" />
                  <input
                    type="text"
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    placeholder="Filter features..."
                    className="w-full pl-9 pr-3 py-2 text-xs bg-[#F6F2EA] border border-[#8C8275]/30 rounded-lg text-[#1E2320] focus:outline-none focus:border-[#2C6E80]"
                  />
                </div>

                <div className="space-y-1.5 max-h-[55vh] overflow-y-auto pr-1">
                  {filteredFeatures.map((feat) => (
                    <button
                      key={feat.id}
                      onClick={() => setSelectedFeatureId(feat.id)}
                      className={`w-full p-3 rounded-xl text-left border transition-all cursor-pointer ${
                        selectedFeatureId === feat.id
                          ? 'bg-[#1E231D] text-white border-[#1E231D] shadow-sm'
                          : 'bg-[#F6F2EA] text-[#1E2320] border-[#8C8275]/20 hover:bg-[#EDE7DB]'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[10px] font-mono mb-1">
                        <span className={selectedFeatureId === feat.id ? 'text-[#64B5F6]' : 'text-[#787165]'}>
                          {feat.badge}
                        </span>
                      </div>
                      <div className="font-serif font-bold text-xs">
                        {feat.title}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Feature Detail Inspector with Screenshot */}
              <div className="lg:col-span-8 space-y-4">
                <div className="p-5 rounded-2xl bg-[#F6F2EA] border border-[#8C8275]/25 space-y-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="text-[10px] font-mono uppercase text-[#2C6E80] font-bold">
                        {selectedFeature.badge}
                      </div>
                      <h3 className="text-xl font-serif font-bold text-[#1E2320]">
                        {selectedFeature.title}
                      </h3>
                    </div>
                    <button
                      onClick={() => handleNavigateAndClose(selectedFeature.view)}
                      className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#2C6E80] hover:bg-[#235866] text-white text-xs font-mono font-semibold transition-colors cursor-pointer shrink-0"
                    >
                      <span>Jump to View</span>
                      <ExternalLink size={13} />
                    </button>
                  </div>

                  <p className="text-xs sm:text-sm text-[#525650] font-serif leading-relaxed">
                    {selectedFeature.summary}
                  </p>

                  {/* Screenshot Preview */}
                  <div className="rounded-xl overflow-hidden border border-[#8C8275]/30 bg-black shadow-xs">
                    <img
                      src={selectedFeature.screenshot}
                      alt={selectedFeature.title}
                      className="w-full object-cover max-h-[260px] hover:scale-102 transition-transform duration-300"
                    />
                  </div>

                  {/* How To Use Steps */}
                  <div className="p-4 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/20">
                    <div className="text-[10px] font-mono uppercase font-bold text-[#787165] mb-2 flex items-center gap-1.5">
                      <CheckCircle2 size={13} className="text-[#3D704D]" />
                      <span>Step-by-Step Instructions</span>
                    </div>
                    <ol className="space-y-1.5 list-decimal list-inside text-xs text-[#1E2320] font-serif">
                      {selectedFeature.howToUse.map((step, idx) => (
                        <li key={idx} className="leading-relaxed">
                          <span className="font-sans font-normal">{step}</span>
                        </li>
                      ))}
                    </ol>
                  </div>

                  {/* Key Highlights */}
                  <div className="p-4 rounded-xl bg-[#EDE7DB]/60 border border-[#8C8275]/20">
                    <div className="text-[10px] font-mono uppercase font-bold text-[#787165] mb-2 flex items-center gap-1.5">
                      <Sparkles size={13} className="text-[#2C6E80]" />
                      <span>Key Architectural Highlights</span>
                    </div>
                    <ul className="space-y-1 text-xs text-[#525650] font-serif">
                      {selectedFeature.keyHighlights.map((hl, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-[#2C6E80] font-bold">•</span>
                          <span>{hl}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: THE 7-STAGE PIPELINE */}
          {activeTab === 'workflow' && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-[#EDE7DB] border border-[#8C8275]/25">
                <div className="text-[10px] font-mono uppercase text-[#787165] font-bold mb-1">
                  SYSTEM ARCHITECTURE
                </div>
                <h3 className="font-serif font-bold text-base text-[#1E2320]">
                  The 7-Stage Deterministic Standards Pipeline
                </h3>
                <p className="text-xs text-[#525650] font-serif leading-relaxed mt-1">
                  NORMVAULT replaces subjective LLM summaries with an auditable, 7-phase evidence engine. Each phase outputs structured data that feeds deterministically into the next.
                </p>
              </div>

              <div className="space-y-3">
                {[
                  {
                    num: '01',
                    name: 'Document Intelligence & Extraction',
                    tech: 'Optical Character Recognition & Regex Parameter Parser',
                    desc: 'Extracts atomic technical requirements from PDFs, scans, and tables, attaching immutable SHA-256 byte offsets.'
                  },
                  {
                    num: '02',
                    name: 'Hybrid Standards Retrieval',
                    tech: 'BM25 Lexical + Dense Vector Reciprocal Rank Fusion (RRF)',
                    desc: 'Searches 22,000+ BIS standards without hallucinating synthetic codes.'
                  },
                  {
                    num: '03',
                    name: 'Deterministic Applicability Engine',
                    tech: '8-Point Factual Evidence Matrix',
                    desc: 'Verifies scope, operating ratings, material grades, tolerances, test conditions, and statutory QCO mandates.'
                  },
                  {
                    num: '04',
                    name: 'Normative Dependency Traversal',
                    tech: 'Directed Acyclic Graph (DAG) Traversal',
                    desc: 'Recursively resolves referenced testing standards, dimensional standards, and companion codes.'
                  },
                  {
                    num: '05',
                    name: 'Currentness, Supersession & QCO Gate',
                    tech: 'BIS Gazette Verification & DPIIT Notifications',
                    desc: 'Detects withdrawn/superseded standards (e.g. IS 325 replaced by IS 12615) and statutory ISI mark obligations.'
                  },
                  {
                    num: '06',
                    name: 'Gap Detection & Corrigendum Formulation',
                    tech: 'Clause Diff Engine & Pre-Tender Corrigendum Generator',
                    desc: 'Highlights ambiguities, conflicting clauses, and produces ready-to-issue addendum text.'
                  },
                  {
                    num: '07',
                    name: 'Procurement Decision Package',
                    tech: 'SHA-256 Cryptographic Digital Seal & End-to-End Traceability Matrix',
                    desc: 'Packages the full legal evidence trail into an unassailable audit-grade memorandum for CVC and CAG.'
                  },
                ].map((stg) => (
                  <div key={stg.num} className="p-4 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25 flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-[#EAE4D8] border border-[#8C8275]/30 text-[#2C6E80] flex items-center justify-center font-mono font-bold text-sm shrink-0">
                      {stg.num}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="font-serif font-bold text-sm text-[#1E2320]">{stg.name}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#E5F0F2] text-[#2C6E80] font-semibold">
                          {stg.tech}
                        </span>
                      </div>
                      <p className="text-xs text-[#525650] font-serif leading-relaxed">
                        {stg.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="text-center pt-2">
                <button
                  onClick={() => handleNavigateAndClose('how-it-works')}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#1E231D] text-white text-xs font-mono font-semibold hover:bg-black transition-colors cursor-pointer"
                >
                  <span>Explore Full Methodology Page</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          )}

          {/* TAB 4: STATUTORY RULES & CHECKLIST */}
          {activeTab === 'glossary' && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-[#EDE7DB] border border-[#8C8275]/25">
                <h3 className="font-serif font-bold text-base text-[#1E2320] mb-1">
                  Public Procurement Statutory Framework
                </h3>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  Every decision in NORMVAULT is cross-referenced against Indian procurement law and vigilance mandates.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-serif">
                <div className="p-4 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25">
                  <div className="font-mono font-bold text-[#2C6E80] uppercase text-[11px] mb-1">
                    Bureau of Indian Standards Act 2016
                  </div>
                  <strong className="block text-[#1E2320] mb-1">Section 16 Mandatory Compliance</strong>
                  <p className="text-[#525650] leading-relaxed">
                    Where the Central Government notifies an Indian Standard under Section 16, no entity may manufacture, import, distribute, or procure goods without the standard mark (ISI mark). Procuring non-ISI goods is an offense.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25">
                  <div className="font-mono font-bold text-[#2C6E80] uppercase text-[11px] mb-1">
                    General Financial Rules (GFR) 2017
                  </div>
                  <strong className="block text-[#1E2320] mb-1">Rule 144(i) Technical Standards</strong>
                  <p className="text-[#525650] leading-relaxed">
                    Mandates that procurement specifications must refer to National Technical Standards (Indian Standards) wherever available. Brand names or restrictive vendor-biased descriptions are prohibited.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25">
                  <div className="font-mono font-bold text-[#2C6E80] uppercase text-[11px] mb-1">
                    DPIIT Quality Control Orders (QCO)
                  </div>
                  <strong className="block text-[#1E2320] mb-1">Mandatory Certification Orders</strong>
                  <p className="text-[#525650] leading-relaxed">
                    Central Ministries (e.g. Heavy Industry, Steel, Chemicals) notify mandatory QCOs. NORMVAULT actively tracks QCO enforcement dates to prevent tenders from omitting mandatory CM/L certification.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25">
                  <div className="font-mono font-bold text-[#2C6E80] uppercase text-[11px] mb-1">
                    Central Vigilance Commission (CVC)
                  </div>
                  <strong className="block text-[#1E2320] mb-1">CVC Guidelines on Tenders & Corrigenda</strong>
                  <p className="text-[#525650] leading-relaxed">
                    Requires that any technical ambiguities, conflicting clauses, or deviations identified during pre-bid meetings must be formally rectified via a gazetted pre-tender Corrigendum with appropriate time extensions.
                  </p>
                </div>
              </div>

              {/* Pre-Tender Checklist */}
              <div className="p-5 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/30">
                <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-3 flex items-center gap-2">
                  <FileCheck size={16} className="text-[#3D704D]" />
                  <span>Pre-Tender Officer's Compliance Checklist</span>
                </h4>
                <div className="space-y-2 text-xs font-sans">
                  {[
                    'Verify that cited standards are CURRENT and not WITHDRAWN or SUPERSEDED.',
                    'Check whether the product falls under any mandatory DPIIT Quality Control Order (QCO).',
                    'Ensure all normative companion testing standards (e.g. bend tests, tensile ratings) are cited.',
                    'Resolve any contradictory parameters between General Specifications and Appendix schedules.',
                    'Generate and publish a pre-tender Corrigendum before the bid submission deadline.',
                    'Archive the cryptographic SHA-256 Decision Package in the procurement file for CVC/CAG audits.'
                  ].map((chk, i) => (
                    <label key={i} className="flex items-start gap-2.5 cursor-pointer text-[#525650]">
                      <input type="checkbox" className="mt-0.5 rounded text-[#2C6E80] focus:ring-[#2C6E80]" />
                      <span>{chk}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Bottom Footer */}
        <div className="px-6 py-3.5 bg-[#EDE7DB] border-t border-[#8C8275]/25 flex items-center justify-between text-xs font-mono">
          <div className="text-[#787165] flex items-center gap-2">
            <span>Tip: Press</span>
            <kbd className="px-1.5 py-0.5 rounded bg-[#FCFAF6] border border-[#8C8275]/30 text-[10px] text-[#1E2320]">
              Esc
            </kbd>
            <span>to close anytime.</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg border border-[#8C8275]/30 hover:bg-[#E2DACB] text-[#1E2320] font-semibold transition-colors cursor-pointer"
            >
              {t('guide_btn_close', 'Close')}
            </button>
            <button
              onClick={() => handleNavigateAndClose('analyze')}
              className="px-4 py-1.5 rounded-lg bg-[#1E231D] hover:bg-black text-white font-semibold transition-colors cursor-pointer flex items-center gap-1.5"
            >
              <span>{t('guide_btn_launch', 'Launch Workspace')}</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
