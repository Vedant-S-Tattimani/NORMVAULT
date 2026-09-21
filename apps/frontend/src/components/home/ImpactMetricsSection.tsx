import React from 'react';
import { TrendingUp, ShieldCheck, Clock, CheckCircle } from 'lucide-react';

export const ImpactMetricsSection: React.FC = () => {
  const metrics = [
    {
      value: '50%',
      label: 'Fewer Tender Ambiguities',
      detail: 'Pre-tender gap detection eliminates contradictory clauses and missing testing parameters before tender publication.',
      icon: TrendingUp,
    },
    {
      value: '40%',
      label: 'Faster Bid Evaluation',
      detail: 'Procurement officers evaluate technical compliance in minutes using automated clause-level traceability matrices.',
      icon: Clock,
    },
    {
      value: '100%',
      label: 'Statutory QCO Compliance',
      detail: 'Mandatory Quality Control Orders under BIS Act Section 16 are automatically enforced across all procurement items.',
      icon: ShieldCheck,
    },
    {
      value: '0',
      label: 'Post-Award Standard Disputes',
      detail: 'Deterministic provenance and normative reference mapping prevent vendor arbitration and CVC audit objections.',
      icon: CheckCircle,
    },
  ];

  return (
    <section id="impact-section" className="py-24 px-6 lg:px-12 bg-[#F6F2EA] border-b border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-2">
            MEASURABLE PROCUREMENT IMPACT
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[#1E2320] leading-tight mb-4">
            Quantifiable Integrity for India's Capital Projects
          </h2>
          <p className="text-sm sm:text-base text-[#525650] font-serif leading-relaxed">
            Delivering measurable time savings, complete legal compliance, and audit-proof documentation 
            for Central Ministries, State Departments, and Public Sector Undertakings.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.label}
                className="bg-[#FCFAF6] rounded-2xl p-8 border border-[#8C8275]/25 shadow-xs flex flex-col justify-between hover:border-[#2C6E80]/40 transition-all"
              >
                <div>
                  <div className="w-10 h-10 rounded-xl bg-[#EAE4D8] border border-[#8C8275]/20 flex items-center justify-center text-[#2C6E80] mb-6">
                    <Icon size={20} />
                  </div>
                  <div className="text-4xl sm:text-5xl font-serif font-black text-[#1E2320] tracking-tight mb-2">
                    {item.value}
                  </div>
                  <div className="font-serif font-bold text-sm text-[#2C6E80] mb-3">
                    {item.label}
                  </div>
                </div>
                <p className="text-xs text-[#525650] font-serif leading-relaxed pt-4 border-t border-[#8C8275]/15">
                  {item.detail}
                </p>
              </div>
            );
          })}
        </div>

        {/* SIH Banner */}
        <div className="mt-12 p-6 rounded-2xl bg-[#EAE4D8]/80 border border-[#8C8275]/30 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-[#1E231D] text-white flex items-center justify-center font-serif font-bold text-lg shrink-0">
              SIH
            </div>
            <div>
              <div className="font-serif font-bold text-sm text-[#1E2320]">
                Smart India Hackathon Problem Statement 26108
              </div>
              <div className="text-xs text-[#525650] font-serif">
                "AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications."
              </div>
            </div>
          </div>
          <div className="text-xs font-mono text-[#787165] bg-[#FCFAF6] px-4 py-2 rounded-lg border border-[#8C8275]/20 shrink-0">
            Authoritative BIS Architecture
          </div>
        </div>
      </div>
    </section>
  );
};
