import React, { useState } from 'react';
import { ViewType } from '../components/common/EditorialHeader';
import {
  ShieldCheck,
  ArrowRight,
  Sparkles,
  Database,
  Cpu,
  Check,
  BookOpen
} from 'lucide-react';

interface HowItWorksPageProps {
  onNavigate: (view: ViewType) => void;
}

export const HowItWorksPage: React.FC<HowItWorksPageProps> = ({ onNavigate }) => {
  const [activeStageIndex, setActiveStageIndex] = useState(0);

  const stages = [
    {
      id: 1,
      number: '01',
      title: 'Document Intelligence & Extraction',
      badge: 'OCR & REGEX PARSING',
      summary: 'Ingests tender PDFs, scans, and technical text to extract atomic requirements with cryptographic offsets.',
      mechanism: 'Layout-aware text decomposition, optical character recognition, and regex parameter extraction for engineering ratings (voltage, yield strength, tolerances, test conditions).',
      whyItMatters: 'Guarantees that every extracted requirement maintains an immutable cryptographic byte-offset (SHA-256) back to the exact page, section, and clause of the original tender PDF.',
      inputs: ['Raw Tender Specification PDF / Scanned Document', 'Section Headings & Appendix Tables'],
      outputs: ['Atomic Requirement Objects with Unique IDs', 'Cryptographic Offset Hashes (e.g., sha256:4f8e...)', 'Extracted Engineering Parameters & Units'],
      sampleData: {
        citation: 'Page 14 / Section 4.2.1 & Appendix Table 2',
        excerpt: 'Motor shall be rated for 415V ± 10%, 50Hz, 3-Phase (Section 4.2), but auxiliary drive motors may operate on 400V nominal (Appendix Table 2). Motors shall conform to IS 325.',
        extractedParams: [
          { name: 'Rated Voltage', value: '415 V (Sec 4.2) / 400 V (Appx Tab 2)' },
          { name: 'Frequency', value: '50 Hz' },
          { name: 'Phase', value: '3-Phase' },
          { name: 'Cited Standard', value: 'IS 325 (Withdrawn)' },
        ],
      },
    },
    {
      id: 2,
      number: '02',
      title: 'Hybrid Standards Retrieval',
      badge: 'BM25 + DENSE VECTOR FUSION',
      summary: 'Combines lexical keyword matching with dense neural vector embeddings across 22,000+ Bureau of Indian Standards.',
      mechanism: 'Lexical BM25 ensures exact standard number retrieval (e.g. "IS 1786"), while dense Sentence-Transformer embeddings capture technical semantic intent (e.g. "TMT rebar", "thermo-mechanically treated bar"). Results are fused via Reciprocal Rank Fusion (RRF).',
      whyItMatters: 'Completely eliminates AI hallucinations by strictly gating candidate standards against the active Bureau of Indian Standards (BIS) catalog database.',
      inputs: ['Extracted Requirement Text & Parameters', 'Authoritative Catalog of 22,000+ BIS Standards'],
      outputs: ['Ranked Candidate Standards with Hybrid Relevance Scores', 'Semantic Intent Embeddings', 'Zero-Hallucination Filtered Candidate Set'],
      sampleData: {
        query: 'Electric motors, 3-Phase, 415V, induction, energy efficiency',
        candidates: [
          { code: 'IS 12615:2018', title: 'Line Operated Three Phase Induction Motors - Specification', score: '0.962 (Rank 1 - BM25 + Vector)' },
          { code: 'IS 15999 (Part 2/Sec 1)', title: 'Standard Methods for Determining Losses and Efficiency from Tests', score: '0.884 (Rank 2 - Vector)' },
          { code: 'IS 325:1996', title: 'Three-Phase Induction Motors (WITHDRAWN / SUPERSEDED)', score: '0.841 (Rank 3 - Lexical Match)' },
        ],
      },
    },
    {
      id: 3,
      number: '03',
      title: 'Deterministic Applicability Engine',
      badge: '8-POINT FACTUAL MATRIX',
      summary: 'Evaluates candidate standards against 8 factual evidence criteria to determine exact applicability without subjective bias.',
      mechanism: 'Rather than trusting generic LLM summaries, the engine systematically verifies 8 deterministic categories: Scope, Operating Parameters, Material Grades, Tolerances, Environmental Conditions, Test Protocols, Safety Guidelines, and Statutory QCO Mandates.',
      whyItMatters: 'Guarantees 100% legal defensibility. If any required engineering criterion is violated or mismatched, the engine flags the exact discrepancy with verbatim factual justification.',
      inputs: ['Candidate Standard Specifications', 'Extracted Tender Requirements', 'Authoritative BIS Scope & Clauses'],
      outputs: ['8-Point Evaluation Matrix (Matched / Unmatched)', 'Confidence Verdict (Applicable / Inapplicable)', 'Verbatim Rationale for Inclusion or Exclusion'],
      sampleData: {
        verdict: 'IS 12615:2018 APPLICABLE (8/8 Criteria Verified)',
        criteriaSample: [
          { category: 'Scope & Product Form', status: 'MATCHED', detail: 'Tender specifies 3-phase squirrel-cage induction motor; IS 12615 Clause 1 covers line-operated 3-phase induction motors.' },
          { category: 'Operating Voltage & Frequency', status: 'MATCHED', detail: 'Tender: 415V, 50Hz; IS 12615 Clause 6.1 standard rated voltage is 415V, 50Hz.' },
          { category: 'Energy Efficiency Class', status: 'MATCHED', detail: 'Tender specifies high efficiency; IS 12615 Clause 7 mandates IE3 minimum efficiency level.' },
          { category: 'Statutory QCO Mandate', status: 'MATCHED', detail: 'DPIIT Electric Motors QCO 2024 mandates IS 12615:2018 with BIS ISI mark.' },
        ],
      },
    },
    {
      id: 4,
      number: '04',
      title: 'Normative Dependency Graph Traversal',
      badge: 'GRAPH INTELLIGENCE',
      summary: 'Recursively unpacks normative references, testing protocols, dimensional codes, and companion standards.',
      mechanism: 'Indian Standards rarely exist in isolation. The engine builds and traverses a directed acyclic graph (DAG) of normative references cited inside the primary standard (e.g. testing codes, sampling frequencies, material specs).',
      whyItMatters: 'Prevents incomplete tender specifications where an authority mandates a product but fails to specify the required destructive testing method or dimensional companion standard.',
      inputs: ['Primary Applicable Indian Standard', 'Normative References Section (Clause 2 of BIS Standard)'],
      outputs: ['Full Dependency Tree of Mandatory Companion Codes', 'Downstream Testing Protocols (Tensile, Bend, Efficiency)', 'Sampling & Tolerance Reference Map'],
      sampleData: {
        primaryCode: 'IS 12615:2018 (Line Operated Induction Motors)',
        dependencies: [
          { refCode: 'IS 15999 (Part 2/Sec 1)', type: 'MANDATORY TEST PROTOCOL', reason: 'Mandated for determining IE3 efficiency and loss measurements.' },
          { refCode: 'IS/IEC 60034-1', type: 'GENERAL PERFORMANCE', reason: 'Rating and performance of rotating electrical machines.' },
          { refCode: 'IS 12065', type: 'PERMISSIBLE NOISE LIMITS', reason: 'Permissible noise levels for rotating electrical machinery.' },
        ],
      },
    },
    {
      id: 5,
      number: '05',
      title: 'Currentness, Supersession & QCO Mandates',
      badge: 'STATUTORY COMPLIANCE GATE',
      summary: 'Tracks standard lifecycle, detects superseded editions, and enforces mandatory DPIIT Quality Control Orders.',
      mechanism: 'Verifies the publication year, active technical amendments (e.g. Amendments 1, 2, 3), and cross-references Section 16 of the BIS Act 2016 and DPIIT Quality Control Orders gazetted by Central Ministries.',
      whyItMatters: 'Procuring items under superseded standards or failing to require the BIS Standard Mark (ISI Mark) for QCO-notified goods violates Indian statutory law. NORMVAULT flags these as BLOCKING.',
      inputs: ['Standard Edition Year', 'Active BIS Amendments Database', 'DPIIT / Ministry Quality Control Orders (QCO)'],
      outputs: ['Edition Currentness Status (Current / Superseded)', 'Active Amendments with Technical Highlights', 'Statutory QCO Enforcement Flag (Mandatory ISI Mark)'],
      sampleData: {
        citedStandard: 'IS 325:1996 (Cited in Tender Section 4.2)',
        status: 'SUPERSEDED & WITHDRAWN BY BIS',
        authoritativeReplacement: 'IS 12615:2018 (Incorporating Amendments 1 & 2)',
        qcoNotification: 'DPIIT Electric Motors (Quality Control) Order 2024 — Mandatory ISI Mark under CM/L license.',
        auditRisk: 'HIGH / BLOCKING — Violates GFR Rule 144(i) and Section 16 of BIS Act 2016.',
      },
    },
    {
      id: 6,
      number: '06',
      title: 'Gap Detection & Corrigendum Formulation',
      badge: 'AUTOMATED RECTIFICATION',
      summary: 'Identifies specification discrepancies, missing tolerances, and generates ready-to-issue pre-tender corrigenda.',
      mechanism: 'Rule-based compliance engine compares tender parameters against the mandated standard to identify ambiguities (e.g. "as per engineer"), contradictory voltages, and missing tolerances. Generates legally sound addendum text.',
      whyItMatters: 'Enables procurement officers to issue a pre-tender corrigendum before bid opening, preventing vendor disputes, delayed technical evaluations, and arbitration claims.',
      inputs: ['Tender Specification Ambiguities', 'Mandated BIS Standard Requirements', 'Clause Reconciliation Engine'],
      outputs: ['Classified Specification Gaps (Blocking / High / Medium)', 'Side-by-Side Clause Diff Inspector', 'Ready-to-Issue Pre-Tender Corrigendum Text'],
      sampleData: {
        gapTitle: 'Conflicting Operating Voltage (415 V vs 400 V Nominal)',
        conflictTenderClause: 'Page 14 states "415 V ± 10%", while Appendix Table 2 specifies "400 V nominal".',
        mandatedStandardClause: 'IS 12615:2018 Clause 6.1 specifies standard rated voltage in India strictly as 415 V, 50 Hz.',
        rectifiedCorrigendumClause: '"Amendment 1: Clause 4.2.1 and Appendix Table 2 are reconciled to specify rated operating voltage strictly as 415 V, 50 Hz, 3-Phase in accordance with IS 12615:2018 Clause 6.1."',
      },
    },
    {
      id: 7,
      number: '07',
      title: 'Procurement Decision Package',
      badge: 'SHA-256 CRYPTOGRAPHIC SEAL',
      summary: 'Synthesizes all intelligence into a tamper-evident decision package with an end-to-end traceability matrix.',
      mechanism: 'Compiles the full Clause Traceability Matrix, applicability evidence, and corrigendum actions into a canonical JSON payload and exports a signed executive memorandum. Computes a live SHA-256 cryptographic seal.',
      whyItMatters: 'Provides unassailable audit defense before the Central Vigilance Commission (CVC), Comptroller and Auditor General (CAG), and Technical Evaluation Committees (TECs).',
      inputs: ['Complete 6-Stage Analysis Payload', 'Canonical JSON Export Schema', 'Statutory Compliance Checklists'],
      outputs: ['End-to-End Clause Traceability Matrix', 'Verifiable SHA-256 Cryptographic Digest', 'Exportable Decision Package (JSON & Printable Memo)'],
      sampleData: {
        runId: 'RUN-2025-0418-NV',
        packageHash: 'a3f89e21b0478dc268153b92ec173491f63e260c2138ad491c10d3215682b84c',
        auditVerdict: 'PROCEED_WITH_CORRIGENDUM',
        traceabilityCount: '18 Clauses Mapped with Verbatim Citations',
        statutoryStatus: '100% CVC & CAG Audit Compliant',
      },
    },
  ];

  const activeStage = stages[activeStageIndex];

  return (
    <div className="bg-[#F6F2EA] min-h-screen text-[#1E2320]">
      {/* Top Header Breadcrumb & Title */}
      <section className="pt-10 pb-8 px-6 lg:px-12 border-b border-[#8C8275]/25 bg-[#EDE7DB]/50">
        <div className="max-w-[1440px] mx-auto">
          <div className="flex items-center gap-2 text-[11px] font-mono text-[#787165] mb-2 uppercase tracking-wider">
            <button
              onClick={() => onNavigate('home')}
              className="hover:text-[#1E2320] transition-colors cursor-pointer"
            >
              Home
            </button>
            <span>/</span>
            <span>Platform Methodology</span>
            <span>/</span>
            <span className="font-bold text-[#1E2320]">The 7-Stage Deterministic Architecture</span>
          </div>

          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#E5F0F2] text-[#2C6E80] text-[10px] font-mono font-semibold uppercase tracking-wider mb-3 border border-[#2C6E80]/30">
                <Sparkles size={12} />
                <span>SIH 26108 • DETERMINISTIC STANDARDS ENGINE</span>
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold text-[#1E2320] leading-tight mb-4">
                How NORMVAULT Works
              </h1>
              <p className="text-sm sm:text-base text-[#525650] font-serif leading-relaxed">
                A seven-stage deterministic intelligence architecture engineered to eliminate specification risks,
                prevent AI hallucinations, and enforce statutory compliance with the <strong>Bureau of Indian Standards (BIS) Act 2016</strong> and <strong>GFR 2017 Rule 144(i)</strong>.
              </p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={() => onNavigate('analyze')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#1E231D] hover:bg-[#0D100C] text-white font-medium text-xs shadow-xs transition-all cursor-pointer"
              >
                <span>Test in Workspace</span>
                <ArrowRight size={13} />
              </button>
              <button
                onClick={() => onNavigate('standards')}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-[#8C8275]/40 hover:bg-[#EAE4D8] text-[#1E2320] font-medium text-xs transition-colors cursor-pointer"
              >
                <BookOpen size={13} />
                <span>Browse Standards</span>
              </button>
            </div>
          </div>

          {/* Quick Metrics Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 pt-6 border-t border-[#8C8275]/20 text-xs font-mono text-[#525650]">
            <div>
              <span className="block text-[10px] text-[#787165] uppercase">STAGES</span>
              <strong className="text-[#1E2320] font-bold text-sm">7 Deterministic Phases</strong>
            </div>
            <div>
              <span className="block text-[10px] text-[#787165] uppercase">EVALUATION GATES</span>
              <strong className="text-[#1E2320] font-bold text-sm">8 Evidence Categories</strong>
            </div>
            <div>
              <span className="block text-[10px] text-[#787165] uppercase">CATALOG COVERAGE</span>
              <strong className="text-[#1E2320] font-bold text-sm">22,000+ BIS Codes</strong>
            </div>
            <div>
              <span className="block text-[10px] text-[#787165] uppercase">AUDIT DEFENSE</span>
              <strong className="text-[#2C6E80] font-bold text-sm">SHA-256 Tamper-Proof</strong>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <section className="py-14 px-6 lg:px-12">
        <div className="max-w-[1440px] mx-auto">
          {/* Section Subhead */}
          <div className="mb-8">
            <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-1">
              PIPELINE DEEP DIVE
            </div>
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-[#1E2320]">
              Step-by-Step Methodology Breakdown
            </h2>
            <p className="text-xs sm:text-sm text-[#525650] font-serif mt-1">
              Select any stage below to inspect its algorithmic mechanism, input/output data, and real-world tender execution.
            </p>
          </div>

          {/* 7-Stage Horizontal Navigation Tabs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 mb-8">
            {stages.map((stg, idx) => (
              <button
                key={stg.id}
                onClick={() => setActiveStageIndex(idx)}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                  activeStageIndex === idx
                    ? 'bg-[#1E231D] text-white border-[#1E231D] shadow-sm'
                    : 'bg-[#FCFAF6] text-[#1E2320] border-[#8C8275]/25 hover:border-[#2C6E80]/50 hover:bg-[#FAF6EE]'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono mb-2">
                  <span className={`font-bold ${activeStageIndex === idx ? 'text-[#2C6E80]' : 'text-[#787165]'}`}>
                    STAGE {stg.number}
                  </span>
                  {activeStageIndex === idx && (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  )}
                </div>
                <div className="font-serif font-bold text-xs line-clamp-2 leading-snug">
                  {stg.title}
                </div>
              </button>
            ))}
          </div>

          {/* Active Stage Detailed Breakdown Card */}
          <div className="bg-[#FCFAF6] rounded-2xl border border-[#8C8275]/30 shadow-xs p-6 sm:p-10 mb-14">
            {/* Stage Title Bar */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-[#8C8275]/20 mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-[#EAE4D8] border border-[#8C8275]/30 text-[#2C6E80] flex items-center justify-center font-serif font-bold text-xl shrink-0">
                  {activeStage.number}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#EFEAE0] text-[#525650] border border-[#8C8275]/25 font-bold">
                      {activeStage.badge}
                    </span>
                    <span className="text-[11px] font-mono text-[#787165]">
                      STAGE {activeStage.number} OF 07
                    </span>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-serif font-bold text-[#1E2320] mt-1">
                    {activeStage.title}
                  </h3>
                </div>
              </div>

              <button
                onClick={() => onNavigate('analyze')}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#2C6E80] hover:bg-[#235866] text-white text-xs font-mono shrink-0 transition-colors shadow-xs cursor-pointer"
              >
                <span>Run Stage in Workspace</span>
                <ArrowRight size={13} />
              </button>
            </div>

            {/* Stage Core Summary */}
            <div className="p-4 rounded-xl bg-[#F6F2EA] border border-[#8C8275]/25 mb-8">
              <div className="text-[10px] font-mono uppercase text-[#787165] font-bold mb-1">
                EXECUTIVE PURPOSE
              </div>
              <p className="text-xs sm:text-sm text-[#1E2320] font-serif leading-relaxed">
                {activeStage.summary}
              </p>
            </div>

            {/* Two-Column Technical Mechanism & Why It Matters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="p-5 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/25">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-[#1E2320] uppercase mb-2">
                  <Cpu size={15} className="text-[#2C6E80]" />
                  <span>Technical & Algorithmic Mechanism</span>
                </div>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  {activeStage.mechanism}
                </p>
              </div>

              <div className="p-5 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/25">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-[#1E2320] uppercase mb-2">
                  <ShieldCheck size={15} className="text-[#2C6E80]" />
                  <span>Why This Matters for Public Tenders</span>
                </div>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  {activeStage.whyItMatters}
                </p>
              </div>
            </div>

            {/* Inputs & Outputs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 text-xs font-mono">
              <div className="p-5 rounded-xl bg-[#EFEAE0]/60 border border-[#8C8275]/25">
                <span className="text-[10px] uppercase text-[#787165] font-bold block mb-3">
                  STAGE INPUTS
                </span>
                <ul className="space-y-2">
                  {activeStage.inputs.map((inp, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-[#2C6E80] font-bold mt-0.5">•</span>
                      <span className="text-[#1E2320] font-sans text-xs">{inp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-5 rounded-xl bg-[#E5F0F2]/50 border border-[#2C6E80]/30">
                <span className="text-[10px] uppercase text-[#2C6E80] font-bold block mb-3">
                  STAGE OUTPUTS & ARTIFACTS
                </span>
                <ul className="space-y-2">
                  {activeStage.outputs.map((outp, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Check size={14} className="text-[#2C6E80] shrink-0 mt-0.5" />
                      <span className="text-[#1E2320] font-sans text-xs font-medium">{outp}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Real-World Tender Execution Sample */}
            <div className="p-5 rounded-xl bg-[#181C17] text-[#FCFAF6] font-mono text-xs">
              <div className="flex items-center justify-between pb-3 border-b border-white/15 mb-3 text-[10px] text-[#A6AEA4] uppercase">
                <span className="flex items-center gap-1.5">
                  <Database size={13} className="text-[#64B5F6]" />
                  <span>Real-World NTPC Thermal Motor Tender Execution</span>
                </span>
                <span className="text-[#64B5F6]">TND-2024-NTPC-ST-088</span>
              </div>
              <pre className="overflow-x-auto text-[11px] text-[#E0DDD5] leading-relaxed font-mono p-2">
                {JSON.stringify(activeStage.sampleData, null, 2)}
              </pre>
            </div>
          </div>

          {/* Statutory Framework Compliance Section */}
          <div className="mb-14">
            <div className="text-center max-w-3xl mx-auto mb-10">
              <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-2">
                STATUTORY FOUNDATIONS
              </div>
              <h3 className="text-2xl sm:text-3xl font-serif font-bold text-[#1E2320]">
                Legal & Regulatory Framework Compliance
              </h3>
              <p className="text-xs sm:text-sm text-[#525650] font-serif mt-1">
                Every stage of NORMVAULT is mapped directly to Indian public procurement law and vigilance guidelines.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="p-6 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/25">
                <div className="text-xs font-mono font-bold text-[#2C6E80] uppercase mb-2">
                  GFR 2017 RULE 144(I)
                </div>
                <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-2">
                  Mandatory Standards Citation
                </h4>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  Mandates that all public procurement technical specifications must explicitly cite Indian Standards wherever available, preventing subjective vendor favoritism.
                </p>
              </div>

              <div className="p-6 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/25">
                <div className="text-xs font-mono font-bold text-[#2C6E80] uppercase mb-2">
                  BIS ACT 2016 SECTION 16
                </div>
                <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-2">
                  Statutory QCO Enforcement
                </h4>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  Empowers Central Ministries to mandate the Standard Mark (ISI Mark). Goods notified under QCOs cannot be manufactured, imported, or procured without BIS certification.
                </p>
              </div>

              <div className="p-6 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/25">
                <div className="text-xs font-mono font-bold text-[#2C6E80] uppercase mb-2">
                  CVC TENDER GUIDELINES
                </div>
                <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-2">
                  Ambiguity Elimination
                </h4>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  Central Vigilance Commission mandates that tender specifications must be clear, objective, and unambiguous to eliminate post-tender disputes and contract arbitration.
                </p>
              </div>

              <div className="p-6 rounded-xl bg-[#FCFAF6] border border-[#8C8275]/25">
                <div className="text-xs font-mono font-bold text-[#2C6E80] uppercase mb-2">
                  MAKE IN INDIA (PPP-MII)
                </div>
                <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-2">
                  Domestic Standards Primacy
                </h4>
                <p className="text-xs text-[#525650] font-serif leading-relaxed">
                  Requires government agencies to prioritize Indian Standards over foreign standards (ASTM, DIN, BS), giving domestic manufacturers fair market access.
                </p>
              </div>
            </div>
          </div>

          {/* Bottom Action CTA */}
          <div className="p-8 sm:p-10 rounded-2xl bg-[#1E231D] text-[#FCFAF6] flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="max-w-xl">
              <h3 className="text-2xl font-serif font-bold text-white mb-2">
                Ready to Validate Your Tender Specifications?
              </h3>
              <p className="text-xs sm:text-sm text-[#D0C9BD] font-serif leading-relaxed">
                Upload your tender PDF or explore the sample NTPC thermal power tender in our interactive workspace.
              </p>
            </div>

            <div className="flex items-center gap-3 shrink-0 flex-wrap">
              <button
                onClick={() => onNavigate('analyze')}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#2C6E80] hover:bg-[#235866] text-white font-medium text-xs sm:text-sm shadow-md transition-colors cursor-pointer"
              >
                <span>Launch Specification Workspace</span>
                <ArrowRight size={14} />
              </button>
              <button
                onClick={() => onNavigate('decision-package')}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-white/20 hover:bg-white/10 text-white font-medium text-xs sm:text-sm transition-colors cursor-pointer"
              >
                <span>View Sample Package</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
