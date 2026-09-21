import React from 'react';
import { ShieldCheck, Building2, Landmark, Award, CheckCircle } from 'lucide-react';

export const EcosystemBanner: React.FC = () => {
  const partners = [
    {
      name: 'Bureau of Indian Standards',
      acronym: 'BIS',
      role: 'National Standards Body of India',
      badge: 'Statutory Authority',
      icon: Award,
    },
    {
      name: 'Government e-Marketplace',
      acronym: 'GeM',
      role: 'National Public Procurement Portal',
      badge: 'Procurement Integration',
      icon: Landmark,
    },
    {
      name: 'DPIIT Ministry of Commerce',
      acronym: 'DPIIT QCO',
      role: 'Quality Control Orders Mandate',
      badge: 'Regulatory Framework',
      icon: ShieldCheck,
    },
    {
      name: 'NTPC & Public Sector Undertakings',
      acronym: 'PSUs',
      role: 'Power, Infrastructure & Rail Tenders',
      badge: 'Enterprise Adoption',
      icon: Building2,
    },
  ];

  return (
    <section id="institutional-ecosystem" className="py-12 px-6 lg:px-12 bg-[#E3DDD0]/70 border-y border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
          <div>
            <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-1">
              INSTITUTIONAL TRUST & STATUTORY COMPLIANCE
            </div>
            <h2 className="text-xl sm:text-2xl font-serif font-bold text-[#1E2320]">
              Engineered for India's Public Procurement Ecosystem
            </h2>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-[#525650] bg-[#EFEAE0] px-3.5 py-1.5 rounded-full border border-[#8C8275]/30">
            <CheckCircle size={13} className="text-[#2C6E80]" />
            <span>Aligned with BIS Act 2016 & GFR Rule 144(i)</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {partners.map((partner) => {
            const Icon = partner.icon;
            return (
              <div
                key={partner.acronym}
                className="bg-[#FCFAF6] p-5 rounded-xl border border-[#8C8275]/25 shadow-xs hover:border-[#2C6E80]/50 hover:shadow-sm transition-all group"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-lg bg-[#EFEAE0] border border-[#8C8275]/20 flex items-center justify-center text-[#2C6E80] group-hover:bg-[#2C6E80] group-hover:text-white transition-colors">
                    <Icon size={18} />
                  </div>
                  <span className="text-[9px] font-mono tracking-wider uppercase px-2 py-0.5 rounded bg-[#EAE4D8] text-[#525650]">
                    {partner.badge}
                  </span>
                </div>
                <div className="font-serif font-bold text-base text-[#1E2320] group-hover:text-[#2C6E80] transition-colors">
                  {partner.acronym}
                </div>
                <div className="text-xs font-medium text-[#4E524C] mt-0.5">
                  {partner.name}
                </div>
                <div className="text-[11px] text-[#787165] mt-2 font-serif leading-relaxed">
                  {partner.role}
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Catalog Health & Statutory Index Bar */}
        <div className="mt-8 p-4 rounded-xl bg-[#EFEAE0] border border-[#8C8275]/25 flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-[#525650]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span className="font-bold text-[#1E2320]">LIVE BIS CATALOG:</span>
            <span>22,418 Active Standards Indexed</span>
          </div>
          <div className="hidden sm:block text-[#8C8275]">•</div>
          <div>
            <strong className="text-[#1E2320]">142</strong> Mandatory DPIIT QCOs Synced
          </div>
          <div className="hidden md:block text-[#8C8275]">•</div>
          <div>
            <strong className="text-[#1E2320]">100%</strong> GFR 144(i) & Make in India Aligned
          </div>
          <div className="hidden lg:block text-[#8C8275]">•</div>
          <div className="text-[11px] text-[#787165]">
            Real-Time Gazettes: <strong className="text-[#2C6E80]">v2026.09 Active</strong>
          </div>
        </div>
      </div>
    </section>
  );
};
