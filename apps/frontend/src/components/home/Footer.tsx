import React from 'react';
import { useTranslation } from 'react-i18next';
import { ArrowUp } from 'lucide-react';
import { ViewType } from '../common/EditorialHeader';

interface FooterProps {
  onNavigate: (view: ViewType) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  const { t } = useTranslation();

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="bg-[#181C17] text-[#D0C9BD] border-t border-[#3A4038] pt-16 pb-12 px-6 lg:px-12 font-sans">
      <div className="max-w-[1440px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-white/10">
          {/* Brand & Purpose Column */}
          <div className="lg:col-span-2">
            <div
              onClick={() => onNavigate('home')}
              className="cursor-pointer flex items-center gap-1 mb-4"
            >
              <span className="text-2xl font-serif font-black tracking-tight text-[#FCFAF6]">
                NORM<span className="text-[#64B5F6] font-sans font-extrabold">VAULT</span>
              </span>
            </div>
            <p className="text-xs text-[#A6AEA4] font-serif leading-relaxed max-w-sm mb-6">
              {t(
                'footer_tagline',
                'An AI-powered recommendation and verification engine for identifying applicable Indian Standards for public procurement specifications, ensuring complete compliance with the BIS Act 2016 and DPIIT QCOs.'
              )}
            </p>
          </div>

          {/* Col 1: Platform */}
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-[#FCFAF6] mb-4">
              {t('footer_platform', 'Platform')}
            </h4>
            <ul className="space-y-2.5 text-xs text-[#A6AEA4]">
              <li>
                <button
                  onClick={() => onNavigate('how-it-works')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('footer_how_it_works', 'How It Works (7 Stages)')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('analyze')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('footer_spec_analysis', 'Specification Analysis')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('footer_standards_catalog', 'Indian Standards Catalog')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('dashboard')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('footer_dashboard', 'Procurement Dashboard')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('decision-package')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('footer_decision_package', 'Decision Package Engine')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('footer_dependency_graph', 'Normative Dependency Graph')}
                </button>
              </li>
            </ul>
          </div>

          {/* Col 2: Statutory Framework */}
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-[#FCFAF6] mb-4">
              {t('footer_statutory', 'Statutory Framework')}
            </h4>
            <ul className="space-y-2.5 text-xs text-[#A6AEA4]">
              <li className="flex items-center gap-1">
                <span>{t('footer_bis_act', 'Bureau of Indian Standards Act 2016')}</span>
              </li>
              <li className="flex items-center gap-1">
                <span>{t('footer_qco_orders', 'DPIIT Quality Control Orders')}</span>
              </li>
              <li className="flex items-center gap-1">
                <span>{t('footer_gfr_144', 'General Financial Rules 2017 (Rule 144)')}</span>
              </li>
              <li className="flex items-center gap-1">
                <span>{t('footer_cvc_guidelines', 'CVC Guidelines on Procurement')}</span>
              </li>
              <li className="flex items-center gap-1">
                <span>{t('footer_gem_mandates', 'GeM Technical Bid Mandates')}</span>
              </li>
            </ul>
          </div>

          {/* Col 3: Standards Divisions */}
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-[#FCFAF6] mb-4">
              {t('footer_divisions', 'Standards Divisions')}
            </h4>
            <ul className="space-y-2.5 text-xs text-[#A6AEA4]">
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('cat_ced', 'Civil & Structural (CED)')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('cat_etd', 'Electrotechnical (ETD)')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('cat_med', 'Mechanical (MED)')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('cat_mtd', 'Metallurgical (MTD)')}
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('standards')}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {t('cat_itd', 'Information Tech (ITD)')}
                </button>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-[#7E887E]">
          <div className="flex flex-wrap items-center gap-4">
            <div>© 2026 NORMVAULT. {t('footer_rights', 'All Rights Reserved.')}</div>
            <span className="hidden sm:inline">•</span>
            <div>{t('footer_viksit', 'Viksit Bharat 2047 Technical Infrastructure')}</div>
          </div>

          <div className="flex items-center gap-6">
            <span className="text-[11px] text-[#A6AEA4]">
              {t('footer_hash_status', 'Deterministic Hash Verification Active')}
            </span>
            <button
              onClick={scrollToTop}
              className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 text-white flex items-center justify-center transition-colors cursor-pointer"
              title={t('footer_scroll_top', 'Scroll to Top')}
            >
              <ArrowUp size={15} />
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
