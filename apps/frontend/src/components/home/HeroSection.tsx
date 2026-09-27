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
    <section
      className="relative w-full overflow-x-hidden bg-[#FAF6EE] select-none border-b border-[#8C8275]/25"
      style={{ height: '100svh', minHeight: '700px', maxHeight: '1100px' }}
    >
      {/* 1. Full-Screen Visual Artwork Background — exact reference canvas: crisp, high contrast, fully opaque */}
      <div
        className="absolute inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: `url('/hero_editorial_canvas.jpg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center 46%',
          backgroundRepeat: 'no-repeat',
        }}
      />

      {/* Left Flanking Editorial Metadata — solid, fully legible, not translucent */}
      <div className="absolute left-6 lg:left-12 top-[44%] -translate-y-1/2 hidden xl:block z-20 pointer-events-none">
        <div className="border-l-2 border-[#1E2320] pl-3 text-[10.5px] tracking-[0.24em] text-[#1E2320] font-serif leading-loose uppercase font-bold">
          <div>{t('pillar_accurate', 'ACCURATE')}</div>
          <div>{t('pillar_compliant', 'COMPLIANT')}</div>
          <div>{t('pillar_transparent', 'TRANSPARENT')}</div>
          <div>{t('pillar_auditable', 'AUDITABLE')}</div>
        </div>
      </div>

      {/* Right Flanking Editorial Metadata — solid, fully legible, not translucent */}
      <div className="absolute right-6 lg:right-12 top-[44%] -translate-y-1/2 hidden xl:block z-20 text-right pointer-events-none">
        <div className="border-r-2 border-[#1E2320] pr-3 text-[10.5px] tracking-[0.24em] text-[#1E2320] font-serif leading-loose uppercase font-bold">
          <div>GFR 144(1)</div>
          <div>BIS ACT 2016</div>
          <div>DPIIT QCOS</div>
          <div>CVC / CAG</div>
        </div>
      </div>

      {/* Bottom Left Corner Signature — solid, legible small caps with divider pipe */}
      <div className="absolute bottom-5 left-6 lg:left-12 z-20 pointer-events-none hidden sm:block">
        <div className="text-[11px] tracking-[0.24em] text-[#FAF6EE] font-serif leading-relaxed uppercase font-bold drop-shadow-[0_1px_2px_rgba(0,0,0,0.85)]">
          | {t('sub_gov', 'BUILT FOR GOVERNMENT AND PSUS')}
        </div>
      </div>

      {/* Bottom Right Corner Signature — solid, legible small caps with divider pipe */}
      <div className="absolute bottom-5 right-6 lg:right-12 z-20 pointer-events-none hidden sm:block">
        <div className="text-[11px] tracking-[0.24em] text-[#FAF6EE] font-serif leading-relaxed uppercase font-bold text-right drop-shadow-[0_1px_2px_rgba(0,0,0,0.85)]">
          {t('sub_bis', 'POWERED BY INDIAN STANDARDS')} |
        </div>
      </div>

      {/* Top Header - Seamlessly Integrated into Artwork */}
      <header className="relative max-w-[1480px] w-full mx-auto px-4 sm:px-6 lg:px-12 pt-5 pb-2 flex items-center justify-between z-30 gap-3">
        {/* Top-Left: Language Switcher & Brand Logo */}
        <div className="flex items-center gap-2.5 sm:gap-4 shrink-0">
          <LanguageSwitcher variant="compact" className="shrink-0" />
          <div
            onClick={() => onNavigate('home')}
            className="cursor-pointer flex items-center gap-0.5 tracking-tight group"
          >
            <span className="text-xl sm:text-2xl lg:text-[1.8rem] font-serif font-semibold text-[#181D1A] group-hover:text-[#1B6A78] transition-colors">
              NORM<span className="text-[#1B6A78] font-serif font-semibold">VAULT</span>
            </span>
          </div>
        </div>

        {/* Center Nav Links (Desktop) */}
        <nav className="hidden md:flex items-center space-x-6 lg:space-x-8 text-[13.5px] font-serif text-[#2B332D] tracking-normal">
          <button
            onClick={() => onNavigate('home')}
            className="text-[#141916] font-semibold border-b-2 border-[#141916] pb-0.5 transition-colors cursor-pointer"
          >
            {t('nav_home', 'Home')}
          </button>
          <button
            onClick={() => onNavigate('standards')}
            className="hover:text-[#141916] transition-colors cursor-pointer"
          >
            {t('nav_standards', 'Standards')}
          </button>
          <button
            onClick={() => onNavigate('analyze')}
            className="hover:text-[#141916] transition-colors cursor-pointer"
          >
            {t('nav_workspace', 'Workspace')}
          </button>
          <button
            onClick={() => onNavigate('dashboard')}
            className="hover:text-[#141916] transition-colors cursor-pointer"
          >
            {t('nav_dashboard', 'Dashboard')}
          </button>
          {onOpenGuide && (
            <button
              onClick={onOpenGuide}
              className="text-[#1B6A78] font-semibold hover:text-[#141916] transition-colors cursor-pointer flex items-center gap-1.5"
            >
              <Compass size={13} />
              <span>{t('nav_user_guide', 'User Guide')}</span>
            </button>
          )}
        </nav>

        {/* Top Right Header Text & Mobile Menu Button */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:block text-right text-[10.5px] md:text-[11px] tracking-[0.22em] text-[#141916] uppercase font-serif font-bold leading-tight">
            | {t('brand_tagline', 'STANDARDS FOR A STRONGER INDIA')}
          </div>

          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="md:hidden p-1.5 rounded-lg border border-[#8C8275]/35 text-[#181D1A] hover:bg-[#EAE4D8]/60 transition-colors cursor-pointer"
            aria-label="Open Navigation Menu"
          >
            <Menu size={20} />
          </button>
        </div>
      </header>

      {/* Mobile Slide-Out Drawer */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/45 backdrop-blur-xs">
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

      {/* Center Editorial Hero Content — positioned in calm upper-middle sky */}
      <div className="relative z-10 flex flex-col items-center w-full px-4 sm:px-6 lg:px-12 mt-[2.5vh] sm:mt-[3.5vh] lg:mt-[4vh]">
        <div className="text-center max-w-3xl mx-auto flex flex-col items-center w-full">
          {/* Eyebrow */}
          <div className="text-[10.5px] sm:text-[11px] md:text-[11.5px] font-serif tracking-[0.24em] text-[#1E2320] uppercase mb-2 sm:mb-2.5 font-bold">
            {t('hero_kicker', 'INDIAN STANDARDS. SMARTER PROCUREMENT.')}
          </div>

          {/* Main Headline — split across exactly two lines */}
          <h1 className="text-[2.2rem] sm:text-[2.9rem] lg:text-[3.5rem] font-serif font-medium tracking-tight leading-[1.08] mb-3 max-w-3xl">
            <span className="block text-[#141A17]">
              {t('hero_title_line1', 'From Specifications to the')}
            </span>
            <span className="block text-[#1B6A78]">
              {t('hero_title_line2', 'Right Standards.')}
            </span>
          </h1>

          {/* Supporting Copy — tight spacing, centered, max-width so it wraps in 2 lines */}
          <p className="text-[12.5px] sm:text-[14px] text-[#222824] leading-[1.55] max-w-[640px] font-serif font-normal text-center mb-3.5 sm:mb-4">
            {t('hero_desc', 'An AI-powered recommendation engine that helps government departments and PSUs identify applicable Indian Standards for accurate, compliant and future-ready procurement specifications.')}
          </p>

          {/* Search & Category — the primary interactive element per the reference */}
          <div className="w-full max-w-[860px] z-30 px-2 sm:px-0">
            {/* Search Bar */}
            <form
              onSubmit={handleHeroSearch}
              className="max-w-[640px] mx-auto relative flex items-center bg-white border border-[#7D766A]/70 hover:border-[#1B6A78] focus-within:border-[#1B6A78] focus-within:ring-2 focus-within:ring-[#1B6A78]/25 rounded-full shadow-[0_2px_8px_rgba(0,0,0,0.06)] transition-all duration-200 overflow-hidden"
            >
              <div className="pl-4 pr-2 text-[#4A544C]">
                <Search size={15} />
              </div>
              <input
                type="text"
                value={heroSearchQuery}
                onChange={(e) => setHeroSearchQuery(e.target.value)}
                placeholder={t('hero_search_placeholder', 'Search standard, equipment, or clause (e.g. IS 12615, 3-Phase Motor)...')}
                className="w-full py-2 sm:py-2.5 text-xs text-[#141916] placeholder-[#666D64] bg-transparent focus:outline-none font-sans"
              />
              <button
                type="submit"
                className="mr-1.5 px-4 py-1.5 rounded-full bg-[#141916] hover:bg-[#1B6A78] text-[#FAF7F0] text-[11px] font-sans font-medium transition-colors flex items-center gap-1 cursor-pointer shrink-0"
              >
                <span>{t('hero_search_btn', 'Search')}</span>
                <ArrowRight size={12} />
              </button>
            </form>

            {/* Category Chips — arranged neatly in exactly 2 rows (5 pills row 1, 2 pills row 2) */}
            <div className="flex flex-col items-center gap-1.5 mt-2.5 text-xs font-sans">
              {/* Row 1: CATEGORIES: + 5 Pills */}
              <div className="flex items-center justify-center gap-1.5 flex-wrap sm:flex-nowrap">
                <span className="text-[9.5px] sm:text-[10px] text-[#3D453E] uppercase font-bold tracking-wider mr-1 shrink-0 font-mono">
                  {t('categories_label', 'CATEGORIES:')}
                </span>
                <button
                  onClick={() => handleChipClick('ETD')}
                  className="px-2.5 py-0.5 sm:py-1 rounded-full bg-[#E5F0F2] hover:bg-[#D5E8EC] text-[#1B6A78] hover:text-[#141916] border border-[#1B6A78]/40 transition-all cursor-pointer whitespace-nowrap text-[10.5px] sm:text-[11px] font-medium shadow-2xs"
                  title="Electrotechnical Standards (ETD)"
                >
                  {t('cat_etd', '⚡ Electrotechnical (ETD)')}
                </button>
                <button
                  onClick={() => handleChipClick('CED')}
                  className="px-2.5 py-0.5 sm:py-1 rounded-full bg-[#FAF5EB] hover:bg-[#F0E8D6] text-[#3D453E] hover:text-[#141916] border border-[#8C8275]/40 transition-all cursor-pointer whitespace-nowrap text-[10.5px] sm:text-[11px] font-medium shadow-2xs"
                  title="Civil & Structural Standards (CED)"
                >
                  {t('cat_ced', '🏛️ Civil & Structural (CED)')}
                </button>
                <button
                  onClick={() => handleChipClick('MED')}
                  className="px-2.5 py-0.5 sm:py-1 rounded-full bg-[#FAF5EB] hover:bg-[#F0E8D6] text-[#3D453E] hover:text-[#141916] border border-[#8C8275]/40 transition-all cursor-pointer whitespace-nowrap text-[10.5px] sm:text-[11px] font-medium shadow-2xs"
                  title="Mechanical Engineering Standards (MED)"
                >
                  {t('cat_med', '⚙️ Mechanical (MED)')}
                </button>
                <button
                  onClick={() => handleChipClick('MTD')}
                  className="px-2.5 py-0.5 sm:py-1 rounded-full bg-[#FAF5EB] hover:bg-[#F0E8D6] text-[#3D453E] hover:text-[#141916] border border-[#8C8275]/40 transition-all cursor-pointer whitespace-nowrap text-[10.5px] sm:text-[11px] font-medium shadow-2xs"
                  title="Metallurgical & Materials Standards (MTD)"
                >
                  {t('cat_mtd', '🔬 Metallurgical (MTD)')}
                </button>
                <button
                  onClick={() => handleChipClick('ITD')}
                  className="px-2.5 py-0.5 sm:py-1 rounded-full bg-[#FAF5EB] hover:bg-[#F0E8D6] text-[#3D453E] hover:text-[#141916] border border-[#8C8275]/40 transition-all cursor-pointer whitespace-nowrap text-[10.5px] sm:text-[11px] font-medium shadow-2xs"
                  title="Information Technology Standards (ITD)"
                >
                  {t('cat_itd', '💻 Information Tech (ITD)')}
                </button>
              </div>

              {/* Row 2: 2 Pills */}
              <div className="flex items-center justify-center gap-1.5 flex-wrap">
                <button
                  onClick={() => handleChipClick('FAD')}
                  className="px-2.5 py-0.5 sm:py-1 rounded-full bg-[#FAF5EB] hover:bg-[#F0E8D6] text-[#3D453E] hover:text-[#141916] border border-[#8C8275]/40 transition-all cursor-pointer whitespace-nowrap text-[10.5px] sm:text-[11px] font-medium shadow-2xs"
                  title="Food and Agriculture Division (FAD)"
                >
                  {t('cat_fad', '🌾 Food & Agriculture (FAD)')}
                </button>
                <button
                  onClick={() => handleChipClick('TXD')}
                  className="px-2.5 py-0.5 sm:py-1 rounded-full bg-[#FAF5EB] hover:bg-[#F0E8D6] text-[#3D453E] hover:text-[#141916] border border-[#8C8275]/40 transition-all cursor-pointer whitespace-nowrap text-[10.5px] sm:text-[11px] font-medium shadow-2xs"
                  title="Textile Division (TXD)"
                >
                  {t('cat_txd', '🧵 Textiles & Fabrics (TXD)')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
