import React from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, Building2, Landmark, Award, CheckCircle } from 'lucide-react';

export const EcosystemBanner: React.FC = () => {
  const { t } = useTranslation();

  const partners = [
    {
      name: t('partner_bis_name', 'Bureau of Indian Standards'),
      acronym: 'BIS',
      role: t('partner_bis_role', 'National Standards Body of India'),
      badge: t('partner_bis_badge', 'Statutory Authority'),
      icon: Award,
    },
    {
      name: t('partner_gem_name', 'Government e-Marketplace'),
      acronym: 'GeM',
      role: t('partner_gem_role', 'National Public Procurement Portal'),
      badge: t('partner_gem_badge', 'Procurement Integration'),
      icon: Landmark,
    },
    {
      name: t('partner_dpiit_name', 'DPIIT Ministry of Commerce'),
      acronym: 'DPIIT QCO',
      role: t('partner_dpiit_role', 'Quality Control Orders Mandate'),
      badge: t('partner_dpiit_badge', 'Regulatory Framework'),
      icon: ShieldCheck,
    },
    {
      name: t('partner_psu_name', 'NTPC & Public Sector Undertakings'),
      acronym: 'PSUs',
      role: t('partner_psu_role', 'Power, Infrastructure & Rail Tenders'),
      badge: t('partner_psu_badge', 'Enterprise Adoption'),
      icon: Building2,
    },
  ];

  return (
    <section id="institutional-ecosystem" className="py-12 px-6 lg:px-12 bg-[#E3DDD0]/70 border-y border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
          <div>
            <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-1">
              {t('eco_kicker', 'INSTITUTIONAL TRUST & STATUTORY COMPLIANCE')}
            </div>
            <h2 className="text-xl sm:text-2xl font-serif font-bold text-[#1E2320]">
              {t('eco_title', "Engineered for India's Public Procurement Ecosystem")}
            </h2>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-[#525650] bg-[#EFEAE0] px-3.5 py-1.5 rounded-full border border-[#8C8275]/30">
            <CheckCircle size={13} className="text-[#2C6E80]" />
            <span>{t('eco_aligned', 'Aligned with BIS Act 2016 & GFR Rule 144(i)')}</span>
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
            <span className="font-bold text-[#1E2320]">{t('eco_live_catalog', 'LIVE BIS CATALOG:')}</span>
            <span>{t('eco_standards_count', '22,418 Active Standards Indexed')}</span>
          </div>
          <div className="hidden sm:block text-[#8C8275]">•</div>
          <div>
            <span>{t('eco_qcos_synced', '142 Mandatory DPIIT QCOs Synced')}</span>
          </div>
          <div className="hidden md:block text-[#8C8275]">•</div>
          <div>
            <span>{t('eco_make_in_india', '100% GFR 144(i) & Make in India Aligned')}</span>
          </div>
          <div className="hidden lg:block text-[#8C8275]">•</div>
          <div className="text-[11px] text-[#787165]">
            <span>{t('eco_audit_seal', 'CVC Provenance Seal Enabled')}</span>
          </div>
        </div>
      </div>
    </section>
  );
};
