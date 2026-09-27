import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertTriangle, CheckCircle2, ArrowRight, Sparkles, FileCode } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface ProblemSectionProps {
  onNavigate: (view: ViewType) => void;
}

export const ProblemSection: React.FC<ProblemSectionProps> = ({ onNavigate }) => {
  const { t } = useTranslation();
  const [selectedSample, setSelectedSample] = useState(0);

  const sampleDemos = [
    {
      title: t('prob_sample_ntpc', 'NTPC Thermal Power Station (Electric Motors)'),
      section: 'Page 14 / Cl 4.2 & Appendix Table 2',
      tenderText: 'Motor shall be rated for 415V ± 10%, 50Hz, 3-Phase (Section 4.2), but auxiliary drive motors may operate on 400V nominal (Appendix Table 2). Motors shall conform to IS 325.',
      conflictReason: 'Appendix Table 2 contradicts Section 4.2 (400V vs 415V); IS 325 is withdrawn by BIS.',
      standardCode: 'IS 12615:2018 (Cl 6.1)',
      standardText: 'Standard rated voltage shall be strictly 415 V at 50 Hz. Single-speed squirrel cage induction motors shall comply with IE3 efficiency limits tested per IS 15999.',
      qcoMandate: 'DPIIT Electric Motors Quality Control Order (Statutory ISI Mark)',
      corrigendumClause: 'Amendment 1: Clause 4.2.1 and Appendix Table 2 are reconciled to specify rated operating voltage strictly as 415 V, 50 Hz, 3-Phase in accordance with IS 12615:2018 Clause 6.1.',
    },
    {
      title: t('prob_sample_nhai', 'NHAI National Highway Project (Structural Steel)'),
      section: 'Section 1000 / Cl 1002.3',
      tenderText: 'All reinforcement bars for RCC culverts and bridges shall be mild steel Grade 1 conforming to IS 432 (Part 1).',
      conflictReason: 'IS 432 is obsolete for major bridge structures; violates Ministry of Steel mandatory QCO.',
      standardCode: 'IS 1786:2008 (Grade Fe 500D)',
      standardText: 'High strength deformed steel bars and wires for concrete reinforcement shall be Fe 500D with minimum elongation 16.0% and mandatory bend test per IS 1599.',
      qcoMandate: 'Ministry of Steel (Quality Control) Order for Reinforcement Bars',
      corrigendumClause: 'Corrigendum 2: Section 1002.3 is amended to specify thermo-mechanically treated (TMT) steel bars conforming strictly to IS 1786:2008 Grade Fe 500D with valid CM/L license.',
    },
  ];

  return (
    <section className="py-20 px-6 lg:px-12 bg-[#EDE8DC] border-b border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        <div className="max-w-3xl mb-14">
          <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-2">
            {t('prob_kicker', 'THE PROCUREMENT VULNERABILITY')}
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[#1E2320] leading-tight mb-4">
            {t('prob_title', 'How Outdated Standards Silently Compromise Public Tenders')}
          </h2>
          <p className="text-sm sm:text-base text-[#525650] font-serif leading-relaxed">
            {t(
              'prob_desc',
              'Over 38% of technical specifications issued by public procurement bodies in India inadvertently cite superseded standards, incomplete testing clauses, or conflict with mandatory DPIIT Quality Control Orders (QCOs)—exposing projects to contractor disputes, cost overruns, and audit scrutiny.'
            )}
          </p>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Legacy Status Quo */}
          <div className="bg-[#F8F4EC] rounded-2xl p-8 border border-red-200/60 shadow-xs relative">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold uppercase tracking-wider text-red-700 mb-6 pb-4 border-b border-red-100">
              <AlertTriangle size={15} className="text-red-600" />
              <span>{t('prob_pitfalls_heading', 'Conventional Procurement Pitfalls')}</span>
            </div>

            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-red-100/70 border border-red-200 text-red-700 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  1
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    {t('prob_pitfall1_title', 'Citing Superseded or Withdrawn Standards')}
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    {t('prob_pitfall1_desc', 'Tenders frequently cite legacy standards like IS 325 for motors instead of the statutory IS 12615:2018 mandated under the mandatory Electric Motors Quality Control Order.')}
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-red-100/70 border border-red-200 text-red-700 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  2
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    {t('prob_pitfall2_title', 'Missing Normative References & Test Procedures')}
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    {t('prob_pitfall2_desc', 'Specifications mandate performance parameters but omit required sampling frequencies, destructive test procedures (e.g. IS 1608), or dimensional companion standards.')}
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-red-100/70 border border-red-200 text-red-700 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  3
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    {t('prob_pitfall3_title', 'DPIIT QCO Non-Compliance & Audit Risk')}
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    {t('prob_pitfall3_desc', 'Inviting tenders without mandatory ISI marking provisions violates Section 16 of the BIS Act 2016, risking CAG objections and legal challenge.')}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* NORMVAULT Solution */}
          <div className="bg-[#FCFAF6] rounded-2xl p-8 border border-[#2C6E80]/40 shadow-xs relative">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold uppercase tracking-wider text-[#2C6E80] mb-6 pb-4 border-b border-[#2C6E80]/15">
              <CheckCircle2 size={15} className="text-[#2C6E80]" />
              <span>{t('prob_sol_heading', 'The NORMVAULT Deterministic Engine')}</span>
            </div>

            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-[#E5F0F2] border border-[#2C6E80]/30 text-[#2C6E80] flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  1
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    {t('prob_sol1_title', 'Automatic Supersession & Legacy Standard Alerts')}
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    {t('prob_sol1_desc', 'Instantly flags obsolete codes and maps them to current active standards with full amendment histories.')}
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-[#E5F0F2] border border-[#2C6E80]/30 text-[#2C6E80] flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  2
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    {t('prob_sol2_title', 'Complete Normative Reference Dependency Graphs')}
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    {t('prob_sol2_desc', 'Recursively extracts every testing method, sampling plan, and companion standard required for watertight tenders.')}
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-7 h-7 rounded-full bg-[#E5F0F2] border border-[#2C6E80]/30 text-[#2C6E80] flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  3
                </div>
                <div>
                  <h4 className="font-serif font-bold text-sm text-[#1E2320] mb-1">
                    {t('prob_sol3_title', 'Cryptographic Audit Defense & Pre-Bid Corrigenda')}
                  </h4>
                  <p className="text-xs text-[#525650] leading-relaxed">
                    {t('prob_sol3_desc', 'Generates ready-to-issue GeM/CPPP corrigendum amendments and SHA-256 sealed audit packages.')}
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
                <span>{t('prob_demo_kicker', 'LIVE CLAUSE RECONCILIATION TEASER')}</span>
              </div>
              <h3 className="text-xl font-serif font-bold text-[#1E2320]">
                {t('prob_demo_title', 'Interactive Technical Reconciliation Demo')}
              </h3>
            </div>
            <span className="text-[11px] font-mono px-3 py-1 rounded-full bg-[#EFEAE0] text-[#525650] border border-[#8C8275]/30">
              {t('prob_demo_desc', 'Inspect how NORMVAULT detects standard conflicts in real tender clauses and generates legally defensible corrigendum amendments.')}
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
              {t('prob_sample_ntpc', 'NTPC Thermal Power Station (Electric Motors)')}
            </button>
            <button
              onClick={() => setSelectedSample(1)}
              className={`px-4 py-2 rounded-lg text-xs font-mono transition-all cursor-pointer whitespace-nowrap ${
                selectedSample === 1
                  ? 'bg-[#1E231D] text-white font-semibold shadow-xs'
                  : 'bg-[#EFEAE0] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/25'
              }`}
            >
              {t('prob_sample_nhai', 'NHAI National Highway Project (Structural Steel)')}
            </button>
          </div>

          {/* Sample Data View */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6 text-xs font-mono">
            {/* Conflicting Tender Text */}
            <div className="rounded-xl bg-status-crimsonBg/30 border border-status-crimsonBorder/70 p-4">
              <div className="flex items-center justify-between text-[10px] text-status-crimson font-bold uppercase mb-2">
                <span>{t('prob_tender_extract', 'TENDER EXTRACT (VULNERABLE CLAUSE)')}</span>
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
                <span>{t('prob_gov_standard', 'GOVERNING INDIAN STANDARD (AUTHORITATIVE)')}</span>
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
                  {t('prob_corrigendum_gen', 'CORRIGENDUM ADDENDUM GENERATED')}
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
              <span>{t('prob_cta_btn', 'Audit Your Specification in Workspace')}</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>

        {/* CTA Bar */}
        <div className="p-6 rounded-xl bg-[#E6DFD2] border border-[#8C8275]/30 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <div className="font-serif font-bold text-base text-[#1E2320]">
              {t('ws_title', 'Technical Specification Audit Workspace')}
            </div>
            <div className="text-xs text-[#525650] mt-0.5 font-serif">
              {t('ws_desc', 'Evidence-backed clause extraction, normative standard identification, and gap detection.')}
            </div>
          </div>
          <button
            onClick={() => onNavigate('analyze')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#1E231D] hover:bg-[#0D100C] text-[#FCFAF6] font-medium text-xs shadow-xs transition-colors shrink-0 cursor-pointer"
          >
            <span>{t('ws_analyze_btn', 'Scan Specification Document')}</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>
    </section>
  );
};
