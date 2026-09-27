import React from 'react';
import { useTranslation } from 'react-i18next';
import { Building, Layers, ShieldCheck, Users, ArrowRight } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface CapabilitiesSectionProps {
  onNavigate: (view: ViewType) => void;
}

export const CapabilitiesSection: React.FC<CapabilitiesSectionProps> = ({ onNavigate }) => {
  const { t } = useTranslation();

  const personas = [
    {
      icon: Building,
      title: t('cap_p1_title', 'Tender Inviting Authorities (TIAs)'),
      role: t('cap_p1_role', 'Chief Engineers & Procurement Officers'),
      description: t(
        'cap_p1_desc',
        'Pre-publication specification review that automatically flags superseded standards (e.g. IS 325 → IS 12615) and generates ready-to-issue corrigendum addenda before NIT release.'
      ),
      action: 'analyze',
      actionLabel: t('cap_p1_btn', 'Scan Tender Specification'),
      stats: t('cap_p1_stat', 'Zero Pre-Bid Corrigenda Delays'),
    },
    {
      icon: Layers,
      title: t('cap_p2_title', 'Technical Evaluation Committees (TECs)'),
      role: t('cap_p2_role', 'Bid Scrutiny & Technical Qualification'),
      description: t(
        'cap_p2_desc',
        'Clause-by-clause traceability matrices mapping bidder technical submittals directly against authoritative BIS requirements, test protocols, and dimensional limits without subjective bias.'
      ),
      action: 'analyze',
      actionLabel: t('cap_p2_btn', 'Inspect Traceability Matrix'),
      stats: t('cap_p2_stat', '40% Faster Technical Evaluation'),
    },
    {
      icon: ShieldCheck,
      title: t('cap_p3_title', 'Vigilance & Audit Authorities'),
      role: t('cap_p3_role', 'Chief Vigilance Officers (CVOs) & CAG'),
      description: t(
        'cap_p3_desc',
        'SHA-256 cryptographic provenance seals locking every evaluation run into an untamperable audit package aligned with CVC guidelines, GFR Rule 144(i), and the BIS Act 2016.'
      ),
      action: 'decision-package',
      actionLabel: t('cap_p3_btn', 'Verify Decision Package'),
      stats: t('cap_p3_stat', 'Cryptographic Audit Defense'),
    },
    {
      icon: Users,
      title: t('cap_p4_title', 'Suppliers, MSMEs & Domestic Industry'),
      role: t('cap_p4_role', 'Fair Bidding & Make in India Access'),
      description: t(
        'cap_p4_desc',
        'Clear, non-ambiguous tender specifications referencing active Indian Standards, eliminating restrictive proprietary clauses and establishing a transparent level playing field.'
      ),
      action: 'standards',
      actionLabel: t('cap_p4_btn', 'Browse Mandated Standards'),
      stats: t('cap_p4_stat', 'Fair & Transparent Bidding'),
    },
  ];

  return (
    <section className="py-24 px-6 lg:px-12 bg-[#EFEAE0] border-b border-[#8C8275]/25">
      <div className="max-w-[1440px] mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
          <div>
            <div className="text-[10px] font-mono tracking-[0.25em] text-[#787165] uppercase mb-2">
              {t('cap_kicker', 'STAKEHOLDER INTEGRATION')}
            </div>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[#1E2320] leading-tight">
              {t('cap_title', 'Engineered for Every Public Procurement Stakeholder')}
            </h2>
          </div>
          <p className="text-sm text-[#525650] max-w-md font-serif leading-relaxed">
            {t(
              'cap_desc',
              "From pre-tender drafting to post-award audit, NORMVAULT provides role-specific rigor for India's procurement ecosystem."
            )}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {personas.map((persona) => {
            const Icon = persona.icon;
            return (
              <div
                key={persona.title}
                className="bg-[#FCFAF6] rounded-2xl p-8 border border-[#8C8275]/30 shadow-xs hover:border-[#2C6E80] transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <div className="w-12 h-12 rounded-xl bg-[#EAE4D8] border border-[#8C8275]/20 flex items-center justify-center text-[#2C6E80] group-hover:bg-[#2C6E80] group-hover:text-white transition-colors">
                      <Icon size={22} />
                    </div>
                    <span className="text-[10px] font-mono font-bold tracking-wider text-[#787165] bg-[#EDE7DB] px-3 py-1 rounded-full border border-[#8C8275]/20">
                      {persona.stats}
                    </span>
                  </div>

                  <div className="text-[11px] font-mono uppercase text-[#2C6E80] font-semibold mb-1">
                    {persona.role}
                  </div>
                  <h3 className="text-xl font-serif font-bold text-[#1E2320] mb-3 group-hover:text-[#2C6E80] transition-colors">
                    {persona.title}
                  </h3>
                  <p className="text-xs sm:text-sm text-[#525650] font-serif leading-relaxed mb-8">
                    {persona.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-[#8C8275]/15 flex items-center justify-between">
                  <button
                    onClick={() => onNavigate(persona.action as ViewType)}
                    className="inline-flex items-center gap-1.5 text-xs font-serif font-semibold text-[#1E2320] hover:text-[#2C6E80] transition-colors cursor-pointer"
                  >
                    <span>{persona.actionLabel}</span>
                    <ArrowRight size={13} className="group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
