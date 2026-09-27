import React, { useState, memo } from 'react';
import { ArrowRight, Search, X, Compass, Menu } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from './LanguageSwitcher';

export type ViewType = 'home' | 'analyze' | 'standards' | 'dashboard' | 'decision-package' | 'how-it-works' | 'benchmarks' | 'comparative';

interface EditorialHeaderProps {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  onOpenGuide?: () => void;
  runId?: string;
}

export const EditorialHeader: React.FC<EditorialHeaderProps> = memo(({
  currentView,
  onSelectView,
  onOpenGuide,
}) => {
  const { t } = useTranslation();
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSelectView('standards');
    }
  };

  const handleNavClick = (view: ViewType) => {
    setIsMobileMenuOpen(false);
    onSelectView(view);
  };

  const navItemClass = (view: ViewType) =>
    `px-2.5 py-1 text-xs font-medium whitespace-nowrap transition-all duration-150 cursor-pointer rounded-md shrink-0 ${
      currentView === view
        ? 'text-[#1E2320] font-semibold bg-[#EAE4D8] shadow-2xs border border-[#8C8275]/25'
        : 'text-[#525650] hover:text-[#1E2320] hover:bg-[#EAE4D8]/50'
    }`;

  const mobileNavItemClass = (view: ViewType) =>
    `flex items-center justify-between w-full px-3.5 py-2.5 text-sm rounded-lg transition-colors cursor-pointer ${
      currentView === view
        ? 'bg-[#EAE4D8] text-[#1E2320] font-bold border border-[#8C8275]/30'
        : 'text-[#4A4E49] hover:bg-[#EAE4D8]/40 hover:text-[#1E2320]'
    }`;

  return (
    <header className="bg-parchment-base border-b border-parchment-border sticky top-0 z-40">
      <div className="max-w-[1540px] mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-2 sm:gap-4">
        {/* Left: Language Switcher, Brand & Navigation */}
        <div className="flex items-center gap-2 sm:gap-4 min-w-0">
          {/* Small button in top-left corner to switch language */}
          <LanguageSwitcher variant="compact" className="shrink-0" />

          <div
            onClick={() => handleNavClick('home')}
            className="cursor-pointer flex items-center gap-1 select-none shrink-0"
          >
            <span className="text-xl sm:text-2xl font-serif font-black tracking-tight text-ink-text whitespace-nowrap">
              NORM<span className="text-mineral-blue font-sans font-extrabold">VAULT</span>
            </span>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 min-w-0">
            <button onClick={() => onSelectView('home')} className={navItemClass('home')}>
              {t('nav_home', 'Home')}
            </button>
            <button onClick={() => onSelectView('standards')} className={navItemClass('standards')}>
              {t('nav_standards', 'Standards')}
            </button>
            <button onClick={() => onSelectView('analyze')} className={navItemClass('analyze')}>
              {t('nav_workspace', 'Workspace')}
            </button>
            <button onClick={() => onSelectView('dashboard')} className={navItemClass('dashboard')}>
              {t('nav_dashboard', 'Dashboard')}
            </button>
            <button onClick={() => onSelectView('decision-package')} className={navItemClass('decision-package')}>
              {t('nav_decision_package', 'Decision Package')}
            </button>
            <button onClick={() => onSelectView('comparative')} className={navItemClass('comparative')}>
              {t('nav_bidder_eval', 'Bidder Evaluation')}
            </button>
            <button onClick={() => onSelectView('benchmarks')} className={navItemClass('benchmarks')}>
              {t('nav_benchmarks', 'Benchmarks')}
            </button>
          </nav>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
          {/* Quick Search */}
          {currentView !== 'standards' && (
            <div className="relative shrink-0">
              {showSearch ? (
                <form onSubmit={handleSearch} className="flex items-center">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search IS..."
                    className="w-28 sm:w-44 px-2 py-1 text-xs bg-parchment-surface border border-parchment-border rounded text-ink-text focus:outline-none focus:border-mineral-blue"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={() => setShowSearch(false)}
                    className="ml-1 text-ink-faint hover:text-ink-text cursor-pointer p-0.5"
                  >
                    <X size={14} />
                  </button>
                </form>
              ) : (
                <button
                  onClick={() => setShowSearch(true)}
                  className="p-1.5 text-ink-muted hover:text-ink-text transition-colors rounded hover:bg-parchment-subtle cursor-pointer"
                  title="Search Standards"
                >
                  <Search size={16} />
                </button>
              )}
            </div>
          )}

          {/* User Guide Button */}
          {onOpenGuide && (
            <button
              onClick={onOpenGuide}
              className="inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1.5 rounded-lg border border-[#2C6E80]/35 bg-[#E5F0F2]/60 hover:bg-[#E5F0F2] text-[#2C6E80] text-xs font-mono font-semibold whitespace-nowrap transition-colors cursor-pointer shrink-0"
              title="Open Interactive User Guide"
            >
              <Compass size={14} />
              <span className="hidden xs:inline sm:inline">{t('nav_user_guide', 'User Guide')}</span>
            </button>
          )}

          {/* Primary Action Button */}
          {currentView !== 'analyze' && (
            <button
              onClick={() => onSelectView('analyze')}
              className="inline-flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3.5 py-1.5 rounded-lg bg-ink-text hover:bg-ink-dark text-parchment-surface text-xs font-semibold whitespace-nowrap shadow-xs transition-colors duration-150 cursor-pointer shrink-0"
            >
              <span className="hidden sm:inline">{t('nav_analyze_btn', 'Analyze Specification')}</span>
              <span className="sm:hidden">{t('nav_analyze_btn', 'Analyze')}</span>
              <ArrowRight size={13} />
            </button>
          )}

          {/* Mobile Hamburger Menu Button (< lg) */}
          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="lg:hidden p-1.5 rounded-lg border border-[#8C8275]/30 text-[#1E2320] hover:bg-[#EAE4D8] transition-colors cursor-pointer ml-1"
            aria-label="Open Navigation Menu"
          >
            <Menu size={19} />
          </button>
        </div>
      </div>

      {/* Mobile Slide-Out Navigation Drawer */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/45 backdrop-blur-xs">
          <div
            className="fixed inset-0"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-hidden="true"
          />
          <div className="relative w-[290px] sm:w-[340px] h-full bg-[#FCFAF6] border-l border-[#8C8275]/30 shadow-2xl p-5 flex flex-col justify-between z-10 overflow-y-auto">
            <div>
              {/* Drawer Header */}
              <div className="flex items-center justify-between pb-3.5 border-b border-[#8C8275]/25 mb-4">
                <span className="text-xl font-serif font-black text-[#1E2320]">
                  NORM<span className="text-[#2C6E80]">VAULT</span>
                </span>
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-1 rounded-md text-[#787165] hover:text-[#1E2320] hover:bg-[#EAE4D8]/60 cursor-pointer"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Drawer Navigation Links */}
              <nav className="space-y-1.5 text-sm font-sans">
                <button onClick={() => handleNavClick('home')} className={mobileNavItemClass('home')}>
                  <span>{t('nav_home', 'Home')}</span>
                </button>
                <button onClick={() => handleNavClick('standards')} className={mobileNavItemClass('standards')}>
                  <span>{t('nav_standards', 'Indian Standards Catalog')}</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-mineral-light text-mineral-dark font-semibold">22K+</span>
                </button>
                <button onClick={() => handleNavClick('analyze')} className={mobileNavItemClass('analyze')}>
                  <span>{t('nav_workspace', 'Specification Workspace')}</span>
                </button>
                <button onClick={() => handleNavClick('dashboard')} className={mobileNavItemClass('dashboard')}>
                  <span>{t('nav_dashboard', 'Executive Dashboard')}</span>
                </button>
                <button onClick={() => handleNavClick('decision-package')} className={mobileNavItemClass('decision-package')}>
                  <span>{t('nav_decision_package', 'Decision Package')}</span>
                </button>
                <button onClick={() => handleNavClick('comparative')} className={mobileNavItemClass('comparative')}>
                  <span>{t('nav_bidder_eval', 'Bidder Evaluation')}</span>
                </button>
                <button onClick={() => handleNavClick('benchmarks')} className={mobileNavItemClass('benchmarks')}>
                  <span>{t('nav_benchmarks', 'Accuracy Benchmarks')}</span>
                </button>
                {onOpenGuide && (
                  <button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      onOpenGuide();
                    }}
                    className="flex items-center justify-between w-full px-3.5 py-2.5 text-sm rounded-lg text-[#2C6E80] font-semibold bg-[#E5F0F2]/70 hover:bg-[#E5F0F2] transition-colors cursor-pointer mt-3"
                  >
                    <div className="flex items-center gap-2">
                      <Compass size={15} />
                      <span>{t('nav_user_guide', 'Interactive User Guide')}</span>
                    </div>
                  </button>
                )}
              </nav>
            </div>

            {/* Drawer Footer */}
            <div className="pt-4 border-t border-[#8C8275]/25 text-[10px] font-mono tracking-widest text-[#787165] uppercase">
              {t('brand_tagline', 'STANDARDS FOR A STRONGER INDIA')}
            </div>
          </div>
        </div>
      )}
    </header>
  );
});
