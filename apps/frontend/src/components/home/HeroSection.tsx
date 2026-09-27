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
    <section className="relative w-full min-h-screen lg:h-screen lg:max-h-[1050px] flex flex-col justify-between overflow-x-hidden bg-[#FAF6EE] select-none border-b border-[#8C8275]/25">
      {/* 1. Full-Screen Visual Artwork Background spanning the ENTIRE Viewport behind Nav, Content & Search */}
      <div
        className="absolute inset-0 bg-cover bg-bottom bg-no-repeat pointer-events-none z-0"
        style={{ backgroundImage: `url('/hero_editorial_canvas.jpg')` }}
      />

      {/* 2. Natural Paper Texture & Fine Grain Overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(#8C8275_0.65px,transparent_0.65px)] [background-size:24px_24px] opacity-10 pointer-events-none z-0" />

      {/* 3. Subtle Edge Watercolor Vignette Blend */}
      <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-[#EAE4D8]/35 to-transparent pointer-events-none z-0" />
      <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-[#FAF6EE]/75 via-[#FAF6EE]/20 to-transparent pointer-events-none z-0" />

      {/* Top Header - Seamlessly Integrated into Artwork */}
      <header className="max-w-[1480px] w-full mx-auto px-4 sm:px-6 lg:px-12 pt-5 pb-2 flex items-center justify-between z-30 shrink-0 gap-3">
        {/* Top-Left: Language Switcher & Brand Logo */}
        <div className="flex items-center gap-2.5 sm:gap-4 shrink-0">
          <LanguageSwitcher variant="compact" className="shrink-0" />
          <div
            onClick={() => onNavigate('home')}
            className="cursor-pointer flex items-center gap-0.5 tracking-tight group"
          >
            <span className="text-xl sm:text-2xl lg:text-[1.8rem] font-serif font-semibold text-[#181D1A] group-hover:text-[#2C6E80] transition-colors">
              NORM<span className="text-[#2C6E80] font-serif font-semibold">VAULT</span>
            </span>
          </div>
        </div>

        {/* Center Nav Links (Desktop) */}
        <nav className="hidden md:flex items-center space-x-6 lg:space-x-8 text-[13px] font-serif text-[#3D453E] tracking-normal">
          <button
            onClick={() => onNavigate('home')}
            className="text-[#181D1A] font-medium border-b border-[#181D1A] pb-0.5 transition-colors cursor-pointer"
          >
            {t('nav_home', 'Home')}
          </button>
          <button
            onClick={() => onNavigate('standards')}
            className="hover:text-[#181D1A] transition-colors cursor-pointer"
          >
            {t('nav_standards', 'Standards')}
          </button>
          <button
            onClick={() => onNavigate('analyze')}
            className="hover:text-[#181D1A] transition-colors cursor-pointer"
          >
            {t('nav_workspace', 'Workspace')}
          </button>
          <button
            onClick={() => onNavigate('dashboard')}
            className="hover:text-[#181D1A] transition-colors cursor-pointer"
          >
            {t('nav_dashboard', 'Dashboard')}
          </button>
          {onOpenGuide && (
            <button
              onClick={onOpenGuide}
              className="text-[#2C6E80] font-medium hover:text-[#181D1A] transition-colors cursor-pointer flex items-center gap-1.5"
            >
              <Compass size={13} />
              <span>{t('nav_user_guide', 'User Guide')}</span>
            </button>
          )}
        </nav>

        {/* Top Right Header Text & Mobile Menu Button */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:block text-right text-[9.5px] md:text-[10px] tracking-[0.24em] text-[#4E564F] uppercase font-serif font-medium leading-tight">
            <div>{t('brand_tagline', 'STANDARDS FOR A STRONGER INDIA')}</div>
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

      {/* Main Hero Container with Flanking Columns & Centerpiece Artwork Integration */}
      <main className="max-w-[1480px] w-full mx-auto px-4 sm:px-6 lg:px-12 flex-1 relative flex flex-col items-center justify-start z-10 min-h-0 pt-4 sm:pt-6 lg:pt-8">
        {/* Left Flanking Editorial Metadata */}
        <div className="absolute left-6 lg:left-12 top-[44%] -translate-y-1/2 hidden xl:block z-20 pointer-events-none">
          <div className="border-l border-[#8C8275]/45 pl-3 text-[9.5px] tracking-[0.24em] text-[#525B53] font-serif leading-loose uppercase font-medium">
            <div>{t('pillar_accurate', 'ACCURATE')}</div>
            <div>{t('pillar_compliant', 'COMPLIANT')}</div>
            <div>{t('pillar_transparent', 'TRANSPARENT')}</div>
            <div>{t('pillar_auditable', 'AUDITABLE')}</div>
          </div>
        </div>

        {/* Right Flanking Editorial Metadata */}
        <div className="absolute right-6 lg:right-12 top-[44%] -translate-y-1/2 hidden xl:block z-20 text-right pointer-events-none">
          <div className="border-r border-[#8C8275]/45 pr-3 text-[9.5px] tracking-[0.24em] text-[#525B53] font-serif leading-loose uppercase font-medium">
            <div>GFR 144(I)</div>
            <div>BIS ACT 2016</div>
            <div>DPIIT QCOS</div>
            <div>CVC / CAG</div>
          </div>
        </div>

        {/* Center Editorial Hero Content */}
        <div className="text-center max-w-3xl mx-auto flex flex-col items-center shrink-0 z-20 relative w-full">
          {/* Eyebrow */}
          <div className="text-[10px] sm:text-[11px] md:text-[12px] font-serif tracking-[0.26em] text-[#4D564E] uppercase mb-2.5 sm:mb-3 font-medium">
            {t('hero_kicker', 'INDIAN STANDARDS. SMARTER PROCUREMENT.')}
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-[3.8rem] font-serif font-normal text-[#141916] tracking-tight leading-[1.14] sm:leading-[1.10] mb-3.5 sm:mb-4 max-w-3xl">
            {t('hero_title', 'From Specifications to the Right Standards.')}
          </h1>

          {/* Supporting Copy */}
          <p className="text-xs sm:text-[13.5px] md:text-[14.5px] text-[#3D453E] leading-[1.65] max-w-[620px] font-serif font-normal text-center mb-5 sm:mb-6">
            {t('hero_desc', 'An AI-powered recommendation engine that helps government departments and PSUs identify applicable Indian Standards for accurate, compliant and future-ready procurement specifications.')}
          </p>

          {/* HERO ACTIONS: Only Two Primary Actions as Requested */}
          <div className="flex items-center justify-center gap-3 sm:gap-4 flex-wrap mb-5 sm:mb-6 z-30">
            {/* PRIMARY: Analyze Specification */}
            <button
              onClick={() => onNavigate('analyze')}
              className="inline-flex items-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 rounded-full bg-[#18201B] hover:bg-[#111713] text-[#FAF7F0] text-xs sm:text-sm font-sans font-medium tracking-wide shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer active:scale-97 group"
            >
              <span>{t('hero_cta_analyze', 'Analyze Specification')}</span>
              <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
            </button>

            {/* SECONDARY: Explore Indian Standards */}
            <button
              onClick={() => onNavigate('standards')}
              className="inline-flex items-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 rounded-full bg-[#FAF6ED]/95 hover:bg-[#FAF6ED] text-[#18201B] border border-[#8C8275]/45 hover:border-[#2C6E80] text-xs sm:text-sm font-sans font-medium tracking-wide shadow-2xs hover:shadow-xs transition-all duration-200 cursor-pointer active:scale-97"
            >
              <span>{t('hero_cta_standards', 'Explore Indian Standards')}</span>
            </button>
          </div>

          {/* Existing Search & Category Functionality - Refined as Subtle Secondary Interaction */}
          <div className="w-full max-w-xl z-30 px-2 sm:px-0">
            {/* Search Bar matching reference composition */}
            <form
              onSubmit={handleHeroSearch}
              className="relative flex items-center bg-[#FAF6ED]/95 hover:bg-[#FAF6ED] border border-[#8C8275]/45 hover:border-[#2C6E80] focus-within:border-[#2C6E80] focus-within:ring-2 focus-within:ring-[#2C6E80]/20 rounded-full shadow-2xs transition-all duration-200 overflow-hidden"
            >
              <div className="pl-4 pr-2 text-[#4A544C]">
                <Search size={15} />
              </div>
              <input
                type="text"
                value={heroSearchQuery}
                onChange={(e) => setHeroSearchQuery(e.target.value)}
                placeholder={t('hero_search_placeholder', 'Search standard, equipment, or clause (e.g. IS 12615, 3-Phase Motor)...')}
                className="w-full py-2 sm:py-2.5 text-xs text-[#181D1A] placeholder-[#666D64]/75 bg-transparent focus:outline-none font-sans"
              />
              <button
                type="submit"
                className="mr-1.5 px-3.5 py-1.5 rounded-full bg-[#18201B] hover:bg-[#2C6E80] text-[#FAF7F0] text-[11px] font-sans font-medium transition-colors flex items-center gap-1 cursor-pointer shrink-0"
              >
                <span>{t('hero_search_btn', 'Search')}</span>
                <ArrowRight size={12} />
              </button>
            </form>

            {/* Category Chips matching reference composition */}
            <div className="flex items-center justify-center gap-1.5 sm:gap-2 flex-wrap mt-2.5 sm:mt-3 text-xs font-sans">
              <span className="text-[10px] text-[#555C54] uppercase font-semibold tracking-wider mr-0.5 shrink-0 font-mono">
                {t('categories_label', 'CATEGORIES:')}
              </span>
              <button
                onClick={() => handleChipClick('ETD')}
                className="px-2.5 py-1 rounded-full bg-[#E5F0F2]/90 hover:bg-[#E5F0F2] text-[#2C6E80] hover:text-[#18201B] border border-[#2C6E80]/35 transition-all cursor-pointer whitespace-nowrap text-[11px] font-medium shadow-2xs"
                title="Electrotechnical Standards (ETD)"
              >
                {t('cat_etd', '⚡ Electrotechnical (ETD)')}
              </button>
              <button
                onClick={() => handleChipClick('CED')}
                className="px-2.5 py-1 rounded-full bg-[#F4EFE5]/90 hover:bg-[#ECE4D6] text-[#4A524A] hover:text-[#18201B] border border-[#8C8275]/35 transition-all cursor-pointer whitespace-nowrap text-[11px] font-medium shadow-2xs"
                title="Civil & Structural Standards (CED)"
              >
                {t('cat_ced', '🏛️ Civil & Structural (CED)')}
              </button>
              <button
                onClick={() => handleChipClick('MED')}
                className="px-2.5 py-1 rounded-full bg-[#F4EFE5]/90 hover:bg-[#ECE4D6] text-[#4A524A] hover:text-[#18201B] border border-[#8C8275]/35 transition-all cursor-pointer whitespace-nowrap text-[11px] font-medium shadow-2xs"
                title="Mechanical Engineering Standards (MED)"
              >
                {t('cat_med', '⚙️ Mechanical (MED)')}
              </button>
              <button
                onClick={() => handleChipClick('MTD')}
                className="px-2.5 py-1 rounded-full bg-[#F4EFE5]/90 hover:bg-[#ECE4D6] text-[#4A524A] hover:text-[#18201B] border border-[#8C8275]/35 transition-all cursor-pointer whitespace-nowrap text-[11px] font-medium shadow-2xs"
                title="Metallurgical & Materials Standards (MTD)"
              >
                {t('cat_mtd', '🔬 Metallurgical (MTD)')}
              </button>
              <button
                onClick={() => handleChipClick('ITD')}
                className="px-2.5 py-1 rounded-full bg-[#F4EFE5]/90 hover:bg-[#ECE4D6] text-[#4A524A] hover:text-[#18201B] border border-[#8C8275]/35 transition-all cursor-pointer whitespace-nowrap text-[11px] font-medium shadow-2xs"
                title="Information Technology Standards (ITD)"
              >
                {t('cat_itd', '💻 Information Tech (ITD)')}
              </button>
              <button
                onClick={() => handleChipClick('FAD')}
                className="px-2.5 py-1 rounded-full bg-[#F4EFE5]/90 hover:bg-[#ECE4D6] text-[#4A524A] hover:text-[#18201B] border border-[#8C8275]/35 transition-all cursor-pointer whitespace-nowrap text-[11px] font-medium shadow-2xs"
                title="Food and Agriculture Division (FAD)"
              >
                {t('cat_fad', '🌾 Food & Agriculture (FAD)')}
              </button>
              <button
                onClick={() => handleChipClick('TXD')}
                className="px-2.5 py-1 rounded-full bg-[#F4EFE5]/90 hover:bg-[#ECE4D6] text-[#4A524A] hover:text-[#18201B] border border-[#8C8275]/35 transition-all cursor-pointer whitespace-nowrap text-[11px] font-medium shadow-2xs"
                title="Textile Division (TXD)"
              >
                {t('cat_txd', '🧵 Textiles & Fabrics (TXD)')}
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Left Corner Signature */}
        <div className="absolute bottom-4 left-6 lg:left-12 z-20 pointer-events-none">
          <div className="border-l border-[#8C8275]/45 pl-3 text-[9.5px] md:text-[10px] tracking-[0.24em] text-[#525B53] font-serif leading-relaxed uppercase font-medium">
            <div>{t('sub_gov', 'BUILT FOR GOVERNMENT AND PSUS')}</div>
          </div>
        </div>

        {/* Bottom Right Corner Signature */}
        <div className="absolute bottom-4 right-6 lg:right-12 z-20 pointer-events-none">
          <div className="border-r border-[#8C8275]/45 pr-3 text-[9.5px] md:text-[10px] tracking-[0.24em] text-[#525B53] font-serif leading-relaxed uppercase font-medium text-right">
            <div>{t('sub_bis', 'POWERED BY INDIAN STANDARDS')}</div>
          </div>
        </div>
      </main>
    </section>
  );
};
