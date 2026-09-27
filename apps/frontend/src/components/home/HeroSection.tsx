import React, { useState } from 'react';
import { X, Menu, Compass, Search, ArrowRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { ViewType } from '../common/EditorialHeader';
import { LanguageSwitcher } from '../common/LanguageSwitcher';

interface HeroSectionProps {
  onNavigate: (view: ViewType, query?: string) => void;
  onOpenGuide?: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onNavigate, onOpenGuide }) => {
  const { t } = useTranslation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [heroSearchQuery, setHeroSearchQuery] = useState('');

  const handleHeroSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (heroSearchQuery.trim()) {
      onNavigate('standards', heroSearchQuery.trim());
    } else {
      onNavigate('standards');
    }
  };

  const handleChipClick = (query: string) => {
    onNavigate('standards', query);
  };

  const handleMobileNav = (view: ViewType) => {
    setIsMobileMenuOpen(false);
    onNavigate(view);
  };

  return (
    <div className="relative w-full min-h-screen bg-[#F6F2EA] flex flex-col justify-between overflow-hidden border-b border-[#8C8275]/25">
      {/* Background Editorial Tint & Fine Grid Overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(#8C8275_0.75px,transparent_0.75px)] [background-size:24px_24px] opacity-15 pointer-events-none" />

      {/* Top Header */}
      <header className="max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-12 pt-5 pb-3 flex items-center justify-between z-30 shrink-0 gap-3">
        {/* Top-Left: Language Switcher and Brand Logo */}
        <div className="flex items-center gap-2 sm:gap-3.5 shrink-0">
          <LanguageSwitcher variant="compact" className="shrink-0" />
          <div
            onClick={() => onNavigate('home')}
            className="cursor-pointer flex items-center gap-0.5 tracking-wide"
          >
            <span className="text-xl sm:text-2xl lg:text-[1.7rem] font-serif font-medium text-[#1E2320]">
              NORM<span className="text-[#2C6E80] font-serif font-medium">VAULT</span>
            </span>
          </div>
        </div>

        {/* Center Nav Links (Desktop) */}
        <nav className="hidden md:flex items-center space-x-6 lg:space-x-8 text-[13px] font-serif text-[#4A4E49] tracking-normal">
          <button
            onClick={() => onNavigate('home')}
            className="text-[#1E2320] font-medium border-b border-[#1E2320] pb-0.5 transition-colors cursor-pointer"
          >
            {t('nav_home', 'Home')}
          </button>
          <button
            onClick={() => onNavigate('standards')}
            className="hover:text-[#1E2320] transition-colors cursor-pointer"
          >
            {t('nav_standards', 'Standards')}
          </button>
          <button
            onClick={() => onNavigate('analyze')}
            className="hover:text-[#1E2320] transition-colors cursor-pointer"
          >
            {t('nav_workspace', 'Workspace')}
          </button>
          <button
            onClick={() => onNavigate('dashboard')}
            className="hover:text-[#1E2320] transition-colors cursor-pointer"
          >
            {t('nav_dashboard', 'Dashboard')}
          </button>
          {onOpenGuide && (
            <button
              onClick={onOpenGuide}
              className="text-[#2C6E80] font-medium hover:text-[#1E2320] transition-colors cursor-pointer flex items-center gap-1"
            >
              <Compass size={13} />
              <span>{t('nav_user_guide', 'User Guide')}</span>
            </button>
          )}
        </nav>

        {/* Top Right Header Text & Mobile Menu Button */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:block text-right text-[9px] md:text-[10px] tracking-[0.22em] text-[#787165] uppercase font-serif leading-tight">
            <div>{t('brand_tagline', 'STANDARDS FOR A STRONGER INDIA')}</div>
          </div>

          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="md:hidden p-1.5 rounded-lg border border-[#8C8275]/30 text-[#1E2320] hover:bg-[#EAE4D8] transition-colors cursor-pointer"
            aria-label="Open Navigation Menu"
          >
            <Menu size={20} />
          </button>
        </div>
      </header>

      {/* Mobile Slide-Out Drawer */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs">
          <div className="w-[280px] sm:w-[320px] h-full bg-[#FCFAF6] border-l border-[#8C8275]/30 shadow-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-[#8C8275]/20 mb-6">
                <div className="flex items-center gap-2">
                  <LanguageSwitcher variant="compact" />
                  <span className="text-xl font-serif font-medium text-[#1E2320]">
                    NORM<span className="text-[#2C6E80]">VAULT</span>
                  </span>
                </div>
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-1 rounded text-[#787165] hover:text-[#1E2320] cursor-pointer"
                >
                  <X size={20} />
                </button>
              </div>

              <nav className="space-y-4 text-sm font-serif">
                <button
                  onClick={() => handleMobileNav('home')}
                  className="block w-full text-left py-1 text-[#1E2320] font-medium border-b border-transparent hover:border-[#1E2320] transition-colors cursor-pointer"
                >
                  {t('nav_home', 'Home')}
                </button>
                <button
                  onClick={() => handleMobileNav('standards')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  {t('nav_standards', 'Standards Catalog')}
                </button>
                <button
                  onClick={() => handleMobileNav('analyze')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  {t('nav_workspace', 'Specification Analysis')}
                </button>
                <button
                  onClick={() => handleMobileNav('dashboard')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  {t('nav_dashboard', 'Procurement Dashboard')}
                </button>
                <button
                  onClick={() => handleMobileNav('decision-package')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  {t('nav_decision_package', 'Decision Package')}
                </button>
                <button
                  onClick={() => handleMobileNav('comparative')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  {t('nav_bidder_eval', 'Bidder Evaluation')}
                </button>
                <button
                  onClick={() => handleMobileNav('benchmarks')}
                  className="block w-full text-left py-1 text-[#4A4E49] hover:text-[#1E2320] transition-colors cursor-pointer"
                >
                  {t('nav_benchmarks', 'Benchmarks & Audits')}
                </button>
                {onOpenGuide && (
                  <button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      onOpenGuide();
                    }}
                    className="block w-full text-left py-1 text-[#2C6E80] font-medium hover:text-[#1E2320] transition-colors cursor-pointer flex items-center gap-1.5"
                  >
                    <Compass size={14} />
                    <span>{t('nav_user_guide', 'User Guide')}</span>
                  </button>
                )}
              </nav>
            </div>

            <div className="pt-4 border-t border-[#8C8275]/20 text-[10px] font-mono tracking-widest text-[#787165] uppercase">
              {t('brand_tagline', 'STANDARDS FOR A STRONGER INDIA')}
            </div>
          </div>
        </div>
      )}

      {/* Main Hero Container with Flanking Columns & Centerpiece */}
      <main className="max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-12 flex-1 relative flex flex-col items-center justify-start z-10 min-h-0 pt-3 sm:pt-6">
        {/* Left & Right Flanking Editorial Metadata (Desktop) */}
        <div className="absolute left-6 lg:left-12 top-[46%] -translate-y-1/2 hidden xl:block z-20">
          <div className="border-l border-[#8C8275]/50 pl-3 text-[9.5px] tracking-[0.22em] text-[#787165] font-serif leading-loose uppercase">
            <div>{t('pillar_accurate', 'ACCURATE')}</div>
            <div>{t('pillar_compliant', 'COMPLIANT')}</div>
            <div>{t('pillar_transparent', 'TRANSPARENT')}</div>
            <div>{t('pillar_auditable', 'AUDITABLE')}</div>
          </div>
        </div>

        <div className="absolute right-6 lg:right-12 top-[46%] -translate-y-1/2 hidden xl:block z-20 text-right">
          <div className="border-r border-[#8C8275]/50 pr-3 text-[9.5px] tracking-[0.22em] text-[#787165] font-serif leading-loose uppercase">
            <div>GFR 144(I)</div>
            <div>BIS ACT 2016</div>
            <div>DPIIT QCOS</div>
            <div>CVC / CAG</div>
          </div>
        </div>

        {/* Center Editorial Hero Content */}
        <div className="text-center max-w-2xl mx-auto flex flex-col items-center shrink-0 z-20 relative w-full">
          {/* Eyebrow */}
          <div className="text-[10.5px] md:text-[11.5px] font-serif tracking-[0.24em] text-[#6E726C] uppercase mb-2">
            {t('hero_kicker', 'INDIAN STANDARDS. SMARTER PROCUREMENT.')}
          </div>

          {/* Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-[3.6rem] font-serif font-normal text-[#1E2320] tracking-normal leading-[1.08] mb-3">
            {t('hero_title', 'From Specifications to the Right Standards.')}
          </h1>

          {/* Subtitle */}
          <p className="text-xs sm:text-[13.5px] md:text-[14.5px] text-[#525650] leading-[1.65] max-w-[560px] font-serif font-normal">
            {t('hero_desc', 'An AI-powered recommendation engine that helps government departments and PSUs identify applicable Indian Standards for accurate, compliant and future-ready procurement specifications.')}
          </p>

          {/* Interactive Standards & Tender Quick-Search Console */}
          <div className="w-full max-w-xl mt-5 z-30 px-2 sm:px-0">
            <form
              onSubmit={handleHeroSearch}
              className="relative flex items-center bg-[#FCFAF6] border border-[#8C8275]/40 hover:border-[#2C6E80] focus-within:border-[#2C6E80] focus-within:ring-2 focus-within:ring-[#2C6E80]/20 rounded-xl shadow-xs transition-all duration-200 overflow-hidden"
            >
              <div className="pl-3.5 pr-2 text-[#2C6E80]">
                <Search size={16} />
              </div>
              <input
                type="text"
                value={heroSearchQuery}
                onChange={(e) => setHeroSearchQuery(e.target.value)}
                placeholder={t('hero_search_placeholder', 'Search standard, equipment, or clause (e.g. IS 12615, 3-Phase Motor)...')}
                className="w-full py-2.5 text-xs text-[#1E2320] placeholder-[#787165]/70 bg-transparent focus:outline-none font-sans"
              />
              <button
                type="submit"
                className="mr-1.5 px-3 py-1.5 rounded-lg bg-[#1E231D] hover:bg-[#2C6E80] text-[#FCFAF6] text-[11px] font-mono font-medium transition-colors flex items-center gap-1 cursor-pointer shrink-0"
              >
                <span>{t('hero_search_btn', 'Search')}</span>
                <ArrowRight size={12} />
              </button>
            </form>

            {/* Categories of Indian Standards */}
            <div className="flex items-center justify-center gap-1.5 sm:gap-2 flex-wrap mt-3 text-xs font-sans">
              <span className="text-[10px] text-[#787165] uppercase font-bold tracking-wider mr-0.5 shrink-0 font-mono">
                {t('categories_label', 'Categories:')}
              </span>
              <button
                onClick={() => handleChipClick('ETD')}
                className="px-2.5 py-1 rounded-full bg-[#E5F0F2]/90 hover:bg-[#E5F0F2] text-[#2C6E80] hover:text-[#1E2320] border border-[#2C6E80]/30 transition-all cursor-pointer whitespace-nowrap text-xs font-medium shadow-2xs hover:shadow-xs"
                title="Electrotechnical Standards (ETD)"
              >
                {t('cat_etd', '⚡ Electrotechnical (ETD)')}
              </button>
              <button
                onClick={() => handleChipClick('CED')}
                className="px-2.5 py-1 rounded-full bg-[#EFEAE0] hover:bg-[#EAE4D8] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/30 transition-all cursor-pointer whitespace-nowrap text-xs font-medium shadow-2xs hover:shadow-xs"
                title="Civil & Structural Standards (CED)"
              >
                {t('cat_ced', '🏛️ Civil & Structural (CED)')}
              </button>
              <button
                onClick={() => handleChipClick('MED')}
                className="px-2.5 py-1 rounded-full bg-[#EFEAE0] hover:bg-[#EAE4D8] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/30 transition-all cursor-pointer whitespace-nowrap text-xs font-medium shadow-2xs hover:shadow-xs"
                title="Mechanical Engineering Standards (MED)"
              >
                {t('cat_med', '⚙️ Mechanical (MED)')}
              </button>
              <button
                onClick={() => handleChipClick('MTD')}
                className="px-2.5 py-1 rounded-full bg-[#EFEAE0] hover:bg-[#EAE4D8] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/30 transition-all cursor-pointer whitespace-nowrap text-xs font-medium shadow-2xs hover:shadow-xs"
                title="Metallurgical & Materials Standards (MTD)"
              >
                {t('cat_mtd', '🔬 Metallurgical (MTD)')}
              </button>
              <button
                onClick={() => handleChipClick('ITD')}
                className="px-2.5 py-1 rounded-full bg-[#EFEAE0] hover:bg-[#EAE4D8] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/30 transition-all cursor-pointer whitespace-nowrap text-xs font-medium shadow-2xs hover:shadow-xs"
                title="Information Technology Standards (ITD)"
              >
                {t('cat_itd', '💻 Information Tech (ITD)')}
              </button>
              <button
                onClick={() => handleChipClick('FAD')}
                className="px-2.5 py-1 rounded-full bg-[#EFEAE0] hover:bg-[#EAE4D8] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/30 transition-all cursor-pointer whitespace-nowrap text-xs font-medium shadow-2xs hover:shadow-xs"
                title="Food and Agriculture Division (FAD)"
              >
                {t('cat_fad', '🌾 Food & Agriculture (FAD)')}
              </button>
              <button
                onClick={() => handleChipClick('TXD')}
                className="px-2.5 py-1 rounded-full bg-[#EFEAE0] hover:bg-[#EAE4D8] text-[#525650] hover:text-[#1E2320] border border-[#8C8275]/30 transition-all cursor-pointer whitespace-nowrap text-xs font-medium shadow-2xs hover:shadow-xs"
                title="Textile Division (TXD)"
              >
                {t('cat_txd', '🧵 Textiles & Fabrics (TXD)')}
              </button>
            </div>
          </div>
        </div>

        {/* Centerpiece Double-Exposure Artwork with Soft Blend & Lift */}
        <div className="w-full flex-1 min-h-0 flex items-end justify-center relative -mt-2 sm:-mt-4 md:-mt-6 pointer-events-none select-none z-10">
          <div className="absolute inset-x-0 top-0 h-16 sm:h-20 bg-gradient-to-b from-[#F6F2EA] via-[#F6F2EA]/60 to-transparent z-10 pointer-events-none" />

          <img
            src="/hero_centerpiece.png"
            alt="Indian Standards, Parliament and Specifications"
            className="w-full max-w-[980px] max-h-[62vh] object-contain object-bottom filter contrast-[1.03] brightness-[1.01]"
          />
        </div>

        {/* Bottom Left Corner Signature */}
        <div className="absolute bottom-4 left-6 lg:left-12 z-20">
          <div className="border-l border-[#8C8275]/50 pl-3 text-[9.5px] md:text-[10px] tracking-[0.22em] text-[#787165] font-serif leading-relaxed uppercase">
            <div>{t('sub_gov', 'BUILT FOR GOVERNMENT AND PSUS')}</div>
          </div>
        </div>

        {/* Bottom Right Corner Signature */}
        <div className="absolute bottom-4 right-6 lg:right-12 z-20">
          <div className="border-l border-[#8C8275]/50 pl-3 text-[9.5px] md:text-[10px] tracking-[0.22em] text-[#787165] font-serif leading-relaxed uppercase text-left">
            <div>{t('sub_bis', 'POWERED BY INDIAN STANDARDS')}</div>
          </div>
        </div>
      </main>
    </div>
  );
};

