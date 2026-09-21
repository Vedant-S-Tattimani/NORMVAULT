import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, ArrowRight, Sparkles, FileCode } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface ProblemSectionProps {
  onNavigate: (view: ViewType) => void;
}

export const ProblemSection: React.FC<ProblemSectionProps> = ({ onNavigate }) => {
  const [selectedSample, setSelectedSample] = useState(0);

  const sampleDemos = [
    {
      title: 'NTPC Thermal Power Station (Electric Motors)',
      section: 'Page 14 / Cl 4.2 & Appendix Table 2',
      tenderText: 'Motor shall be rated for 415V ± 10%, 50Hz, 3-Phase (Section 4.2), but auxiliary drive motors may operate on 400V nominal (Appendix Table 2). Motors shall conform to IS 325.',
      conflictReason: 'Appendix Table 2 contradicts Section 4.2 (400V vs 415V); IS 325 is withdrawn by BIS.',
      standardCode: 'IS 12615:2018 (Cl 6.1)',
      standardText: 'Standard rated voltage shall be strictly 415 V at 50 Hz. Single-speed squirrel cage induction motors shall comply with IE3 efficiency limits tested per IS 15999.',
      qcoMandate: 'DPIIT Electric Motors Quality Control Order 2024 (Statutory ISI Mark)',
      corrigendumClause: 'Amendment 1: Clause 4.2.1 and Appendix Table 2 are reconciled to specify rated operating voltage strictly as 415 V, 50 Hz, 3-Phase in accordance with IS 12615:2018 Clause 6.1.',
    },
    {
      title: 'NHAI National Highway Project (Structural Steel)',
      section: 'Section 1000 / Cl 1002.3',
      tenderText: 'All reinforcement bars for RCC culverts and bridges shall be mild steel Grade 1 conforming to IS 432 (Part 1).',
      conflictReason: 'IS 432 is obsolete for major bridge structures; violates Ministry of Steel mandatory QCO.',
      standardCode: 'IS 1786:2008 (Grade Fe 500D)',
      standardText: 'High strength deformed steel bars and wires for concrete reinforcement shall be Fe 500D with minimum elongation 16.0% and mandatory bend test per IS 1599.',
      qcoMandate: 'Ministry of Steel (Quality Control) Order 2024 for Reinforcement Bars',
      corrigendumClause: 'Corrigendum 2: Section 1002.3 is amended to specify thermo-mechanically treated (TMT) steel bars conforming strictly to IS 1786:2008 Grade Fe 500D with valid CM/L license.',
    },
  ];

  return (
    <section className="py-20 px-6 lg:px-12 bg-[#EDE8DC] border-b border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        <div className="max-w-3xl mb-14">
          <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-2">
            THE PROCUREMENT VULNERABILITY
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[#1E2320] leading-tight mb-4">
            How Outdated Standards Silently Compromise Public Tenders
          </h2>
          <p className="text-sm sm:text-base text-[#525650] font-serif leading-relaxed">
            Over 38% of technical specifications issued by public procurement bodies in India inadvertently 
            cite superseded standards, incomplete testing clauses, or conflict with mandatory 
            DPIIT Quality Control Orders (QCOs)—exposing projects to contractor disputes, cost overruns, and audit scrutiny.
          </p>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Legacy Status Quo */}
          <div className="bg-[#F8F4EC] rounded-2xl p-8 border border-red-200/60 shadow-xs relative">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold uppercase tracking-wider text-red-700 mb-6 pb-4 border-b border-red-100">
              <AlertTriangle size={15} className="text-red-600" />
              <span>Conventional Procurement Pitfalls</span>
            </div>

            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-red-100/70 border border-red-200 text-red-700 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  1
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    Citing Superseded or Withdrawn Standards
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    Tenders frequently cite legacy standards like <code>IS 325</code> for motors instead of the statutory 
                    <code>IS 12615:2018</code> mandated under the mandatory Electric Motors Quality Control Order.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-red-100/70 border border-red-200 text-red-700 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  2
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    Missing Normative References & Test Procedures
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    Specifications mandate performance parameters but omit required sampling frequencies, 
                    destructive test procedures (e.g. <code>IS 1608</code>), or dimensional companion standards.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-red-100/70 border border-red-200 text-red-700 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  3
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    Disputes, Delayed Evaluations & Audit Objections
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    Ambiguous standard citations trigger pre-bid queries, contested technical evaluations, 
                    and adverse audit observations by the CVC and CAG.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* NORMVAULT Solution */}
          <div className="bg-[#FCFAF6] rounded-2xl p-8 border border-[#2C6E80]/40 shadow-xs relative">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold uppercase tracking-wider text-[#2C6E80] mb-6 pb-4 border-b border-[#2C6E80]/15">
              <CheckCircle2 size={15} className="text-[#2C6E80]" />
              <span>The NORMVAULT Deterministic Engine</span>
            </div>

            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-[#E5F0F2] border border-[#2C6E80]/30 text-[#2C6E80] flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  1
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    Deterministic Currentness & QCO Enforcement
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    Automatically verifies active BIS editions, detects superseded citations, and flags statutory 
                    mandatory Quality Control Orders under the BIS Act 2016.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-[#E5F0F2] border border-[#2C6E80]/30 text-[#2C6E80] flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  2
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    Complete Standards Dependency Graph Unpacking
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    Recursively traverses normative references, dimensional tolerances, and test methods to 
                    ensure your tender specification is 100% self-contained and auditable.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-[#E5F0F2] border border-[#2C6E80]/30 text-[#2C6E80] flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  3
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    Cryptographically Sealed Decision Package
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    Generates a SHA-256 signed traceability matrix mapping every specification requirement to 
                    exact BIS clauses for tamper-proof audit defense.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Live Clause Reconciliation Teaser */}
        <div className="mb-12 bg-[#FCFAF6] rounded-2xl border border-[#8C8275]/35 p-6 sm:p-8 shadow-xs">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#8C8275]/20 mb-6">
            <div>
              <div className="flex items-center gap-2 text-[10px] font-mono tracking-widest text-[#2C6E80] uppercase font-bold mb-1">
                <Sparkles size={13} className="text-[#2C6E80]" />
                <span>INTERACTIVE ENGINE PREVIEW</span>
              </div>
              <h3 className="text-xl font-serif font-bold text-[#1E2320]">
                See How NORMVAULT Reconciles Contradictory Tender Clauses
              </h3>
            </div>
            <span className="text-[11px] font-mono px-3 py-1 rounded-full bg-[#EFEAE0] text-[#525650] border border-[#8C8275]/30">
              Live Reconciliation Demo
            </span>
          </div>

          {/* Sample Selector Tabs */}
          <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-1">
            <button
              onClick={() => setSelectedSample(0)}
              className={`px-4 py-2 rounded-lg text-xs font-mono transition-all cursor-pointer whitespace-nowrap ${
                selectedSample === 0
                  ? 'bg-[#1E231D] text-white font-semibold shadow-xs'
                  : 'bg-[#EFEAE0] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/25'
              }`}
            >
              Sample 1: NTPC Thermal Motor Tender (IS 325 vs IS 12615)
            </button>
            <button
              onClick={() => setSelectedSample(1)}
              className={`px-4 py-2 rounded-lg text-xs font-mono transition-all cursor-pointer whitespace-nowrap ${
                selectedSample === 1
                  ? 'bg-[#1E231D] text-white font-semibold shadow-xs'
                  : 'bg-[#EFEAE0] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/25'
              }`}
            >
              Sample 2: NHAI Bridge Infrastructure (IS 432 vs IS 1786)
            </button>
          </div>

          {/* Sample Data View */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6 text-xs font-mono">
            {/* Conflicting Tender Text */}
            <div className="rounded-xl bg-status-crimsonBg/30 border border-status-crimsonBorder/70 p-4">
              <div className="flex items-center justify-between text-[10px] text-status-crimson font-bold uppercase mb-2">
                <span>CONVENTIONAL TENDER CITATION (CONFLICTING)</span>
                <span>{sampleDemos[selectedSample].section}</span>
              </div>
              <p className="text-ink-text font-serif italic text-xs leading-relaxed mb-3">
                "{sampleDemos[selectedSample].tenderText}"
              </p>
              <div className="text-[11px] text-status-crimson pt-2 border-t border-status-crimsonBorder/50">
                ⚠ {sampleDemos[selectedSample].conflictReason}
              </div>
            </div>

            {/* Authoritative Standard & QCO */}
            <div className="rounded-xl bg-status-sageBg/30 border border-status-sageBorder/70 p-4">
              <div className="flex items-center justify-between text-[10px] text-status-sage font-bold uppercase mb-2">
                <span>AUTHORITATIVE BIS STANDARD (MANDATED)</span>
                <span>{sampleDemos[selectedSample].standardCode}</span>
              </div>
              <p className="text-ink-text font-serif text-xs leading-relaxed mb-3">
                {sampleDemos[selectedSample].standardText}
              </p>
              <div className="text-[11px] text-status-sage pt-2 border-t border-status-sageBorder/50">
                ✓ {sampleDemos[selectedSample].qcoMandate}
              </div>
            </div>
          </div>

          {/* Rectified Corrigendum Banner */}
          <div className="p-4 rounded-xl bg-[#EFEAE0] border border-[#8C8275]/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <FileCode size={18} className="text-[#2C6E80] shrink-0 mt-0.5" />
              <div>
                <span className="text-[10px] font-mono uppercase text-[#787165] font-bold block mb-0.5">
                  NORMVAULT RECTIFIED PRE-TENDER CORRIGENDUM CLAUSE
                </span>
                <p className="text-xs font-serif text-[#1E2320] italic">
                  "{sampleDemos[selectedSample].corrigendumClause}"
                </p>
              </div>
            </div>

            <button
              onClick={() => onNavigate('analyze')}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#2C6E80] hover:bg-[#235866] text-white text-xs font-mono shrink-0 transition-colors shadow-xs cursor-pointer"
            >
              <span>Test in Workspace</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>

        {/* CTA Bar */}
        <div className="p-6 rounded-xl bg-[#E6DFD2] border border-[#8C8275]/30 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <div className="font-serif font-bold text-base text-[#1E2320]">
              Have an active tender specification document?
            </div>
            <div className="text-xs text-[#525650] mt-0.5 font-serif">
              Upload your PDF or text to run the 7-stage deterministic standards verification.
            </div>
          </div>
          <button
            onClick={() => onNavigate('analyze')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#1E231D] hover:bg-[#0D100C] text-[#FCFAF6] font-medium text-xs shadow-xs transition-colors shrink-0 cursor-pointer"
          >
            <span>Scan Specification Document</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>
    </section>
  );
};
